
import logging
from datetime import datetime, timedelta
from typing import Dict

from src.core.glpi_client import GLPIClient
from .utils import clean_str, clean_html, get_int, parse_date, clean_usuario_nome, get_campo_name
from .core import fetch_with_backoff

logger = logging.getLogger(__name__)

def sync_ticket_changes(client: GLPIClient, session, models: Dict, valid_ids: Dict, limit: int = None, since_date: datetime = None):
    """
    Sync Ticket History (Logs).
    Handles differences between DTIC and SIS TicketChange models dynamically.
    """
    logger.info(f"🚀 Syncing Ticket Changes...{f' [LIMIT={limit}]' if limit else ''}{f' [SINCE={since_date}]' if since_date else ''}")
    TicketModel = models['Ticket']
    TicketChange = models['TicketChange']
    
    # Pre-load tickets map (glpi_id -> db_id)
    tickets_map = {t.glpi_id: t.id for t in session.query(TicketModel.glpi_id, TicketModel.id).all()}
    
    # Determine model capabilities
    has_usuario_nome = hasattr(TicketChange, 'usuario_nome')
    has_campo_id = hasattr(TicketChange, 'campo_id')
    
    range_start = 0
    range_step = 5000  # Logs can be huge
    total_changes = 0
    max_date_mod = None
    
    while True:
        if limit and total_changes >= limit: break
        
        # Filter logs for Tickets
        criteria = {
            'criteria[0][field]': 'itemtype',
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': 'Ticket',
            'sort': 'id',
            'order': 'ASC'
        }
        
        if since_date:
            # Add date filter for logs
            # Note: 'date_mod' in Log table usually represents the event time
            criteria['criteria[1][link]'] = 'AND'
            criteria['criteria[1][field]'] = 'date_mod'
            criteria['criteria[1][searchtype]'] = 'morethan'
            criteria['criteria[1][value]'] = since_date.strftime('%Y-%m-%d %H:%M:%S')
        
        result = fetch_with_backoff(client, 'Log', criteria, range_start, range_step)
        if result == 0: break
        logs = result
        if not logs: break
        
        for log in logs:
            if limit and total_changes >= limit: break
            glpi_id = log.get('id') # Log ID
            ticket_glpi_id = get_int(log.get('items_id'))
            
            # Check if ticket exists in our DB
            # Check if ticket exists in our DB
            if not ticket_glpi_id: continue
            
            if ticket_glpi_id not in tickets_map:
                # 🚨 ORPHAN DETECTED (Dead Letter Queue)
                # Store it to retry later when ticket might exist
                OrphanChange = models.get('OrphanChange')
                if OrphanChange:
                    # Check if already in DLQ to avoid dupes in DLQ
                    existing_orphan = session.query(OrphanChange).filter_by(glpi_log_id=glpi_id).first()
                    if not existing_orphan:
                        orphan = OrphanChange(
                            glpi_log_id=glpi_id,
                            glpi_ticket_id=ticket_glpi_id,
                            context=client.context if hasattr(client, 'context') else 'unknown', # Context logic needed
                            payload=log,
                            created_at=datetime.utcnow()
                        )
                        session.add(orphan)
                continue
            
            db_ticket_id = tickets_map[ticket_glpi_id]
            
            # Check if change already exists
            existing = session.query(TicketChange).filter_by(glpi_id=glpi_id).first()
            if existing:
                continue
            
            # Prepare data
            data = {
                'glpi_id': glpi_id,
                'ticket_id': db_ticket_id,
                'data_mudanca': parse_date(log.get('date_mod')),
                'usuario_id': get_int(log.get('users_id')),  # ✅ Sempre armazena, mesmo se deletado
                'campo': clean_str(log.get('field')) or get_campo_name(get_int(log.get('id_search_option'))),
                'valor_antigo': clean_html(log.get('old_value')),  # ✅ Decodifica HTML
                'valor_novo': clean_html(log.get('new_value')),    # ✅ Decodifica HTML
                'sincronizado_em': datetime.now()
            }
            
            # Validations for specific fields
            if data['campo'] == 'content': continue # Skip heavy content logs if needed, or keep
            
            # Add extra fields for DTIC if they exist
            if has_usuario_nome:
                data['usuario_nome'] = clean_usuario_nome(log.get('user_name'))  # ✅ Remove "(ID)"
            if has_campo_id:
                data['campo_id'] = get_int(log.get('id_search_option')) or 0  # ✅ Extrai da API 
            
            change = TicketChange(**data)
            session.add(change)
        
        session.commit()
        # Clear Identity Map to free memory (critical for large log datasets)
        session.expunge_all()
        
        total_changes += len(logs)
        
        # Cursor Update
        current_max = max([parse_date(l.get('date_mod')) for l in logs if l.get('date_mod')], default=None)
        if current_max:
            if not max_date_mod or current_max > max_date_mod:
                max_date_mod = current_max
                
        if len(logs) > 0:
            logger.info(f"   Processed {total_changes} logs... (Max Date: {max_date_mod})")
        
        range_start += len(logs)

    logger.info(f"   ✅ Total Changes Synced: {total_changes}")
    return max_date_mod


def reprocess_orphan_changes(session, models: Dict, context: str, limit: int = 500, base_backoff_minutes: int = 5):
    """
    Reprocessa mudanças órfãs com backoff e limite por lote.
    """
    OrphanChange = models.get('OrphanChange')
    if not OrphanChange:
        return {"processed": 0, "skipped": 0, "remaining": 0}
    TicketModel = models['Ticket']
    TicketChange = models['TicketChange']
    now = datetime.utcnow()

    orphans = (
        session.query(OrphanChange)
        .filter_by(context=context)
        .order_by(OrphanChange.created_at.asc())
        .limit(limit)
        .all()
    )

    tickets_map = {t.glpi_id: t.id for t in session.query(TicketModel.glpi_id, TicketModel.id).all()}

    processed = 0
    skipped = 0

    for orphan in orphans:
        delay = timedelta(minutes=base_backoff_minutes * (2 ** min(orphan.attempt_count or 0, 6)))
        if orphan.last_attempt and orphan.last_attempt + delay > now:
            skipped += 1
            continue

        payload = orphan.payload or {}
        glpi_id = orphan.glpi_log_id
        ticket_glpi_id = orphan.glpi_ticket_id

        orphan.attempt_count = (orphan.attempt_count or 0) + 1
        orphan.last_attempt = now

        if ticket_glpi_id not in tickets_map:
            continue

        existing = session.query(TicketChange).filter_by(glpi_id=glpi_id).first()
        if existing:
            session.delete(orphan)
            processed += 1
            continue

        has_usuario_nome = hasattr(TicketChange, 'usuario_nome')
        has_campo_id = hasattr(TicketChange, 'campo_id')

        data = {
            'glpi_id': glpi_id,
            'ticket_id': tickets_map[ticket_glpi_id],
            'data_mudanca': parse_date(payload.get('date_mod')),
            'usuario_id': get_int(payload.get('users_id')),
            'campo': clean_str(payload.get('field')) or get_campo_name(get_int(payload.get('id_search_option'))),
            'valor_antigo': clean_html(payload.get('old_value')),
            'valor_novo': clean_html(payload.get('new_value')),
            'sincronizado_em': datetime.now()
        }

        if data['campo'] == 'content':
            session.delete(orphan)
            processed += 1
            continue

        if has_usuario_nome:
            data['usuario_nome'] = clean_usuario_nome(payload.get('user_name'))
        if has_campo_id:
            data['campo_id'] = get_int(payload.get('id_search_option')) or 0

        change = TicketChange(**data)
        session.add(change)
        session.delete(orphan)
        processed += 1

    session.commit()
    remaining = session.query(OrphanChange).filter_by(context=context).count()
    return {"processed": processed, "skipped": skipped, "remaining": remaining}
