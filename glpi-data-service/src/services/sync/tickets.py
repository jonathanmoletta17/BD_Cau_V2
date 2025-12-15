
import logging
from datetime import datetime
from typing import Dict, Type

from src.core.glpi_client import GLPIClient
from .utils import clean_str, clean_html, get_int, parse_date, calc_hash
from .core import fetch_with_backoff

logger = logging.getLogger(__name__)

def sync_tickets(client: GLPIClient, session, models: Dict, valid_ids: Dict, context: str = 'dtic', limit: int = None, since_date: datetime = None):
    logger.info(f"🚀 Syncing Tickets ({context.upper()})...{f' [LIMIT={limit}]' if limit else ''}{f' [SINCE={since_date}]' if since_date else ''}")
    
    if limit: logger.info(f"   ⚠️ Limit applied: {limit}")
    
    TicketModel = models['Ticket']
    TicketUser = models.get('TicketUser')
    TicketGroup = models.get('TicketGroup')

    # Debug Valid IDs
    v_ent = len(valid_ids.get('entities', []))
    logger.info(f"   🔍 Context: {context}, Valid Entities: {v_ent}")

    range_start = 0
    range_step = 100
    total = 0
    max_date_mod = None
    
    # Base criteria
    criteria = {'expand_dropdowns': 'false'}
    
    # Incremental filter
    if since_date:
        criteria['criteria[0][field]'] = 'date_mod'
        criteria['criteria[0][searchtype]'] = 'morethan'
        criteria['criteria[0][value]'] = since_date.strftime('%Y-%m-%d %H:%M:%S')
    
    while True:
        if limit and total >= limit: break
        
        result = fetch_with_backoff(client, 'Ticket', criteria, range_start, range_step)
        
        if result == 0: 
            break
            
        tickets = result
        if not tickets: break
        
        for t in tickets:
            if limit and total >= limit: break
            glpi_id = t.get('id')
            
            # Check exist
            existing = session.query(TicketModel).filter_by(glpi_id=glpi_id).first()
            
            # Validation
            ent_id = get_int(t.get('entities_id'))
            if ent_id and ent_id not in valid_ids['entities']: ent_id = None
            
            cat_id = get_int(t.get('itilcategories_id'))
            if cat_id and cat_id not in valid_ids['categories']: cat_id = None
            
            loc_id = get_int(t.get('locations_id'))
            if loc_id and loc_id not in valid_ids['locations']: loc_id = None
            
            # Dynamic Logic for 'ultimo_atualizador_id' (DTIC only)
            ua_id = get_int(t.get('users_id_lastupdater'))
            if ua_id and ua_id not in valid_ids['users']: ua_id = None
            
            data = {
                'glpi_id': glpi_id,
                'titulo': clean_str(t.get('name', ''))[:500] if t.get('name') else None,
                'descricao': clean_html(t.get('content')),
                'status_id': get_int(t.get('status')),
                'prioridade_id': get_int(t.get('priority')),
                'tipo_id': get_int(t.get('type')),
                'impact': get_int(t.get('impact')),
                'urgency': get_int(t.get('urgency')),
                'categoria_id': cat_id,
                'entidade_id': ent_id,
                'localizacao_id': loc_id,
                'tipo_requisicao_id': get_int(t.get('requesttypes_id')),
                'criado_em': parse_date(t.get('date')),
                'atualizado_em': parse_date(t.get('date_mod')),
                'solucionado_em': parse_date(t.get('solvedate')),
                'fechado_em': parse_date(t.get('closedate')),
                'tempo_para_resolver': get_int(t.get('time_to_resolve')),
                'tempo_para_atribuir': get_int(t.get('time_to_own')),
                'ticket_hash': calc_hash(t),
                'url': f"{client.base_url.replace('/apirest.php', '')}/front/ticket.form.php?id={glpi_id}",
                'is_deleted': t.get('is_deleted') == 1,
                'sincronizado_em': datetime.now()
            }
            
            # Handle model variations
            has_versao = hasattr(TicketModel, 'versao')
            if has_versao:
                data['versao'] = 1
                data['ultimo_atualizador_id'] = ua_id
                data['tempo_primeira_interacao'] = get_int(t.get('takeintoaccount_delay_stat'))
                data['tempo_acao_total'] = get_int(t.get('actiontime'))

            ticket_obj = None
            if existing:
                for k, v in data.items():
                    if k != 'criado_em':
                        setattr(existing, k, v)
                ticket_obj = existing
            else:
                ticket_obj = TicketModel(**data)
                session.add(ticket_obj)
            
            # --- Inline Actor Processing (TicketUser/TicketGroup) ---
            if TicketUser and TicketGroup:
                # Flush to ensure ticket_obj.id is available
                if not existing:
                    session.flush() 
                
                tid = ticket_obj.id
                
                # Helper to upsert actor
                def upsert_user(uid, type_id):
                    if not uid or uid <= 0: return
                    if uid not in valid_ids['users']: return
                    
                    ex_actor = session.query(TicketUser).filter_by(ticket_id=tid, user_id=uid, type=type_id).first()
                    if not ex_actor:
                        tu = TicketUser(ticket_id=tid, user_id=uid, type=type_id, sincronizado_em=datetime.now())
                        session.add(tu)

                def upsert_group(gid, type_id):
                    if not gid or gid <= 0: return
                    if gid not in valid_ids['groups']: return
                    
                    ex_actor = session.query(TicketGroup).filter_by(ticket_id=tid, group_id=gid, type=type_id).first()
                    if not ex_actor:
                        tg = TicketGroup(ticket_id=tid, group_id=gid, type=type_id, sincronizado_em=datetime.now())
                        session.add(tg)

                # Type 1: Requester, 2: Assignee, 3: Observer
                upsert_user(get_int(t.get('_users_id_requester')), 1)
                upsert_user(get_int(t.get('_users_id_assign')), 2)
                upsert_user(get_int(t.get('_users_id_observer')), 3)
                
                upsert_group(get_int(t.get('_groups_id_assign')), 2)
                upsert_group(get_int(t.get('_groups_id_observer')), 3)

            # --- RAG Integration (Embeddings) ---
            # Automatically learn from ticket content
            # Only for DTIC context for now as configured in KnowledgeService imports (it imports dtic Ticket)
            # Future improvement: Make KnowledgeService context-aware or generic
            if context == 'dtic':
                try:
                    from src.modules.dtic.knowledge.service import KnowledgeService
                    ks = KnowledgeService()
                    # commit=False because we pledge to commit the whole batch at loop end
                    ks.learn_ticket_sync(session, glpi_id, commit=False)
                except Exception as e:
                    logger.warning(f"   ⚠️ RAG Optimization failed for Ticket {glpi_id}: {e}")

        
        session.commit()
        total += len(tickets)
        
        # Cursor Update: Track max date
        # Note: GLPI API sorts by ID by default if not specified, so we scan result for max date
        current_max = max([parse_date(t.get('date_mod')) for t in tickets if t.get('date_mod')], default=None)
        if current_max:
            if not max_date_mod or current_max > max_date_mod:
                max_date_mod = current_max
        
        logger.info(f"   Processed {total} tickets... (Max Date: {max_date_mod})")
        range_start += len(tickets)
        
    logger.info(f"   ✅ Total Tickets Synced: {total}")
    return max_date_mod

def sync_ticket_actors(client: GLPIClient, session, models: Dict, valid_ids: Dict, limit: int = None):
    # Generic implementation for TicketUser / TicketGroup
    # Assuming models dict has 'Ticket', 'TicketUser', 'TicketGroup'
    logger.info(f"🚀 Syncing Ticket Actors...{f' [LIMIT={limit}]' if limit else ''}")
    TicketModel = models['Ticket']
    TicketUser = models['TicketUser']
    TicketGroup = models['TicketGroup']
    
    tickets_map = {t.glpi_id: t.id for t in session.query(TicketModel.glpi_id, TicketModel.id).all()}
    valid_u = valid_ids['users']
    valid_g = valid_ids['groups']
    
    # 1. Users
    range_start = 0
    range_step = 2000
    count_u = 0
    
    while True:
        if limit and count_u >= limit: break
        
        result = fetch_with_backoff(client, 'Ticket_User', {}, range_start, range_step)
        if result == 0: break
        actors = result
        if not actors: break
        
        for a in actors:
            if limit and count_u >= limit: break
            tid = int(a.get('tickets_id'))
            uid = int(a.get('users_id'))
            atype = int(a.get('type', 1))
            
            if uid not in valid_u or tid not in tickets_map: continue
            
            existing = session.query(TicketUser).filter_by(
                ticket_id=tickets_map[tid], user_id=uid, type=atype
            ).first()
            
            if not existing:
                tu = TicketUser(
                    ticket_id=tickets_map[tid], user_id=uid, type=atype,
                    sincronizado_em=datetime.now()
                )
                session.add(tu)
                count_u += 1
        session.commit()
        range_start += len(actors)
        
    # 2. Groups
    range_start = 0
    count_g = 0
    while True:
        if limit and count_g >= limit: break
        
        result = fetch_with_backoff(client, 'Group_Ticket', {}, range_start, range_step)
        if result == 0: break
        actors = result
        if not actors: break
        
        for a in actors:
            if limit and count_g >= limit: break
            tid = int(a.get('tickets_id'))
            gid = int(a.get('groups_id'))
            atype = int(a.get('type', 2))
            
            if gid not in valid_g or tid not in tickets_map: continue
            
            existing = session.query(TicketGroup).filter_by(
                ticket_id=tickets_map[tid], group_id=gid, type=atype
            ).first()
            if not existing:
                tg = TicketGroup(
                    ticket_id=tickets_map[tid], group_id=gid, type=atype,
                    sincronizado_em=datetime.now()
                )
                session.add(tg)
                count_g += 1
        session.commit()
        range_start += len(actors)
        
    logger.info("   ✅ Ticket Actors synced.")

def sync_ticket_items(client: GLPIClient, session, models: Dict, valid_ids: Dict, limit: int = None):
    """Sync Ticket-Item links (Assets)."""
    logger.info(f"🚀 Syncing Ticket Items...{f' [LIMIT={limit}]' if limit else ''}")
    TicketModel = models['Ticket']
    TicketItem = models['TicketItem']
    
    tickets_map = {t.glpi_id: t.id for t in session.query(TicketModel.glpi_id, TicketModel.id).all()}
    
    range_start = 0
    range_step = 2000
    count = 0
    
    while True:
        if limit and count >= limit: break
        
        result = fetch_with_backoff(client, 'Item_Ticket', {}, range_start, range_step)
        if result == 0: break
        links = result
        if not links: break
        
        for l in links:
            if limit and count >= limit: break
            tid = int(l.get('tickets_id'))
            itemtype = l.get('itemtype')
            items_id = int(l.get('items_id'))
            
            if tid not in tickets_map: continue
            
            # glpi_items_tickets usually has 'id'.
            link_id = l.get('id')
            
            existing = session.query(TicketItem).filter_by(id=link_id).first()
            if not existing:
                ti = TicketItem(
                    id=link_id,
                    tickets_id=tickets_map[tid], 
                    itemtype=itemtype,
                    items_id=items_id,
                    sincronizado_em=datetime.now()
                )
                session.merge(ti)
                count += 1
        session.commit()
        range_start += len(links)
        
    logger.info("   ✅ Ticket Items synced.")
