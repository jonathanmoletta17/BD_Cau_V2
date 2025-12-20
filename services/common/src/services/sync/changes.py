
import logging
from datetime import datetime
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
