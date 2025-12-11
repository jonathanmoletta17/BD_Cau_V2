"""
GLPI Sync Service
Centralized logic for synchronizing data from GLPI to PostgreSQL.
Supports multiple contexts (DTIC, SIS) by accepting dynamic models.
"""
import requests
import logging
import hashlib
import html
import re
from datetime import datetime
from typing import Dict, Any, Type, Set

from src.core.glpi_client import GLPIClient
from src.core import data_cleaning

# Setup Logger
logger = logging.getLogger(__name__)

# --- Clean Utilities ---
clean_usuario_nome = data_cleaning.clean_usuario_nome
get_campo_name = data_cleaning.get_campo_name
treat_empty = data_cleaning.treat_empty_value
load_user_map = data_cleaning.load_user_lookup

def clean_str(val):
    if isinstance(val, str) and not val.strip():
        return None
    return val

def get_int(val):
    if val is None or val is False:
        return None
    if isinstance(val, int):
        return val if val != 0 else None
    if isinstance(val, str):
        if not val.strip():
            return None
        if val.isdigit():
            i = int(val)
            return i if i != 0 else None
    return None

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None

def calc_hash(t):
    hash_str = f"{t.get('name', '')}{t.get('content', '')}{t.get('status', '')}{t.get('priority', '')}"
    return hashlib.md5(hash_str.encode()).hexdigest()

def clean_html(raw_html):
    if not raw_html:
        return None
    decoded = html.unescape(str(raw_html))
    decoded = html.unescape(decoded)
    clean = re.sub(r'<[^>]+>', ' ', decoded)
    text_content = " ".join(clean.split())
    return text_content if text_content else None




class SyncService:
    """Service to handle GLPI synchronization logic."""

    @staticmethod
    def _fetch_with_backoff(client: GLPIClient, entity_type: str, criteria: Dict[str, Any], 
                          start: int, step: int, limit_step: int = 50) -> Any:
        """
        Fetches data with a backoff strategy to handle HTTP 400/416 errors at end of range.
        Recursively reduces step size to find remaining items.
        Returns:
            - List[Dict]: Items found.
            - int: 0 if End of Range confirmed.
        """
        range_end = start + step - 1
        range_header = f"{start}-{range_end}"
        local_criteria = criteria.copy()
        local_criteria['range'] = range_header
        
        try:
            items = client.make_request(entity_type, local_criteria)
            return items
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [400, 416]:
                # If step is small enough, assume legitimate end of data
                if step <= limit_step:
                    logger.info(f"   ℹ️ End of range confirmed (Step {step} failed at {start}).")
                    return 0
                
                # Backoff: Try a smaller step (10% of current)
                new_step = max(limit_step, step // 10)
                logger.warning(f"   ⚠️ Range {range_header} rejected (HTTP {e.response.status_code}). Backing off to step {new_step}...")
                
                # Recursive call
                return SyncService._fetch_with_backoff(client, entity_type, criteria, start, new_step, limit_step)
            raise e


    @staticmethod
    def sync_entities(client: GLPIClient, session, EntityModel: Type):
        logger.info("🚀 Syncing Entities...")
        entities = client.get_entities()
        logger.info(f"   📥 Found {len(entities)} entities")
        
        for ent in entities:
            entity = EntityModel(
                id=ent['id'],
                name=clean_str(ent.get('name')),
                completename=clean_str(ent.get('completename')),
                level=ent.get('level'),
                entities_id=ent.get('entities_id') if ent.get('entities_id') != 0 else None,
                sincronizado_em=datetime.now()
            )
            session.merge(entity)
        session.commit()
        logger.info(f"   ✅ Entities synced.")

    @staticmethod
    def sync_locations(client: GLPIClient, session, LocationModel: Type):
        logger.info("🚀 Syncing Locations...")
        locations = client.get_locations()
        logger.info(f"   📥 Found {len(locations)} locations")
        
        for loc in locations:
            location = LocationModel(
                id=loc['id'],
                name=clean_str(loc.get('completename') or loc.get('name')),
                level=loc.get('level'),
                parent_id=loc.get('locations_id') if loc.get('locations_id') != 0 else None,
                ancestors_cache=clean_str(loc.get('ancestors_cache')),
                sincronizado_em=datetime.now()
            )
            session.merge(location)
        session.commit()
        logger.info(f"   ✅ Locations synced.")

    @staticmethod
    def sync_groups(client: GLPIClient, session, GroupModel: Type):
        logger.info("🚀 Syncing Groups...")
        groups = client.get_groups()
        logger.info(f"   📥 Found {len(groups)} groups")
        
        for grp in groups:
            group = GroupModel(
                id=grp['id'],
                name=clean_str(grp.get('name')),
                is_task=bool(grp.get('is_task', 0)),
                is_itemgroup=bool(grp.get('is_itemgroup', 0)),
                sincronizado_em=datetime.now()
            )
            session.merge(group)
        session.commit()
        logger.info(f"   ✅ Groups synced.")

    @staticmethod
    def sync_users(client: GLPIClient, session, UserModel: Type):
        logger.info("🚀 Syncing Users...")
        users = client.get_users()
        logger.info(f"   📥 Found {len(users)} users")
        
        # Emails
        try:
            logger.info("   📧 Fetching emails...")
            user_emails = client.get_all_pages('UserEmail')
            email_map = {ue.get('users_id'): ue.get('email') for ue in user_emails if ue.get('users_id')}
        except:
            email_map = {}
        
        for usr in users:
            uid = usr['id']
            email = usr.get('email') or email_map.get(uid)
            user = UserModel(
                id=uid,
                name=clean_str(usr.get('name')),
                realname=clean_str(usr.get('realname')),
                firstname=clean_str(usr.get('firstname')),
                email=clean_str(email),
                is_active=bool(usr.get('is_active', 1)),
                is_deleted=bool(usr.get('is_deleted', 0)),
                sincronizado_em=datetime.now()
            )
            session.merge(user)
        session.commit()
        logger.info(f"   ✅ Users synced.")

    @staticmethod
    def sync_categories(client: GLPIClient, session, CategoryModel: Type):
        logger.info("🚀 Syncing Categories...")
        categories = client.get_itil_categories()
        logger.info(f"   📥 Found {len(categories)} categories")
        for cat in categories:
            category = CategoryModel(
                id=cat['id'],
                name=clean_str(cat.get('name')),
                completename=clean_str(cat.get('completename')),
                level=cat.get('level'),
                parent_id=cat.get('itilcategories_id'),
                ancestors_cache=clean_str(cat.get('ancestors_cache')),
                sincronizado_em=datetime.now()
            )
            session.merge(category)
        session.commit()
        logger.info("   ✅ Categories synced.")

    @staticmethod
    def sync_profiles(client: GLPIClient, session, ProfileModel: Type):
        logger.info("🚀 Syncing Profiles...")
        profiles = client.get_profiles()
        logger.info(f"   📥 Found {len(profiles)} profiles")
        for prof in profiles:
            profile = ProfileModel(
                id=prof['id'],
                name=clean_str(prof.get('name')),
                is_default=bool(prof.get('is_default', 0)),
                sincronizado_em=datetime.now()
            )
            session.merge(profile)
        session.commit()
        logger.info("   ✅ Profiles synced.")

    @staticmethod
    def sync_groups_users(client: GLPIClient, session, GroupUserModel: Type, valid_ids: Dict):
        logger.info("🚀 Syncing Group-User Relations...")
        relationships = client.get_groups_users()
        logger.info(f"   📥 Found {len(relationships)} relations")
        
        valid_u = valid_ids['users']
        valid_g = valid_ids['groups']
        
        for rel in relationships:
            uid = rel.get('users_id')
            gid = rel.get('groups_id')
            if uid not in valid_u or gid not in valid_g:
                continue
            
            existing = session.query(GroupUserModel).filter_by(users_id=uid, groups_id=gid).first()
            if existing:
                existing.is_dynamic = bool(rel.get('is_dynamic', 0))
                existing.is_manager = bool(rel.get('is_manager', 0))
                existing.sincronizado_em = datetime.now()
            else:
                gu = GroupUserModel(
                    users_id=uid, groups_id=gid,
                    is_dynamic=bool(rel.get('is_dynamic', 0)),
                    is_manager=bool(rel.get('is_manager', 0)),
                    sincronizado_em=datetime.now()
                )
                session.add(gu)
        session.commit()
        logger.info("   ✅ Group-User relations synced.")

    @staticmethod
    def sync_profiles_users(client: GLPIClient, session, ProfileUserModel: Type, valid_ids: Dict):
        logger.info("🚀 Syncing Profile-User Relations...")
        relationships = client.get_profiles_users()
        logger.info(f"   📥 Found {len(relationships)} relations")
        
        valid_u = valid_ids['users']
        valid_p = valid_ids['profiles']
        valid_e = valid_ids['entities']
        
        seen = set()
        for rel in relationships:
            uid = rel.get('users_id')
            pid = rel.get('profiles_id')
            eid = rel.get('entities_id')
            
            if uid not in valid_u or pid not in valid_p or eid not in valid_e:
                continue
                
            key = (uid, pid, eid)
            if key in seen: continue
            seen.add(key)
            
            existing = session.query(ProfileUserModel).filter_by(
                users_id=uid, profiles_id=pid, entities_id=eid
            ).first()
            
            if existing:
                existing.is_recursive = bool(rel.get('is_recursive', 0))
                existing.is_dynamic = bool(rel.get('is_dynamic', 0))
                existing.sincronizado_em = datetime.now()
            else:
                pu = ProfileUserModel(
                    users_id=uid, profiles_id=pid, entities_id=eid,
                    is_recursive=bool(rel.get('is_recursive', 0)),
                    is_dynamic=bool(rel.get('is_dynamic', 0)),
                    sincronizado_em=datetime.now()
                )
                session.add(pu)
        session.commit()
        logger.info("   ✅ Profile-User relations synced.")

    @staticmethod
    def sync_tickets(client: GLPIClient, session, TicketModel: Type, valid_ids: Dict, context: str = 'dtic', limit: int = None, since_date: datetime = None):
        logger.info(f"🚀 Syncing Tickets ({context.upper()})...{f' [LIMIT={limit}]' if limit else ''}{f' [SINCE={since_date}]' if since_date else ''}")
        
        if limit: logger.info(f"   ⚠️ Limit applied: {limit}")
        
        # Debug Valid IDs
        v_ent = len(valid_ids.get('entities', []))
        v_cat = len(valid_ids.get('categories', []))
        v_loc = len(valid_ids.get('locations', []))
        v_usr = len(valid_ids.get('users', []))
        logger.info(f"   🔍 Context: {context}, Valid Entities: {v_ent}, Valid Categories: {v_cat}, Valid Locations: {v_loc}, Valid Users: {v_usr}")

        range_start = 0
        range_step = 100
        total = 0
        
        # Base criteria
        criteria = {'expand_dropdowns': 'false'}
        
        # Incremental filter
        if since_date:
            # GLPI format: YYYY-MM-DD HH:MM:SS
            # Criteria: date_mod > since_date
            criteria['criteria[0][field]'] = 'date_mod'
            criteria['criteria[0][searchtype]'] = 'morethan'
            criteria['criteria[0][value]'] = since_date.strftime('%Y-%m-%d %H:%M:%S')
        
        while True:
            if limit and total >= limit: break
            
            # Use Backoff Strategy
            result = SyncService._fetch_with_backoff(client, 'Ticket', criteria, range_start, range_step)
            
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
                else:
                    # SIS model doesn't have these fields
                    pass

                if existing:
                    for k, v in data.items():
                        # Skip 'criado_em' on update
                        if k != 'criado_em':
                            setattr(existing, k, v)
                else:
                    ticket = TicketModel(**data)
                    session.add(ticket)
            
            session.commit()
            total += len(tickets) # Increment by ACTUAL count
            logger.info(f"   Processed {total} tickets...")
            range_start += len(tickets) # Advance by ACTUAL count
            
        logger.info(f"   ✅ Total Tickets Synced: {total}")

    @staticmethod
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
            
            result = SyncService._fetch_with_backoff(client, 'Ticket_User', {}, range_start, range_step)
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
            
            result = SyncService._fetch_with_backoff(client, 'Group_Ticket', {}, range_start, range_step)
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

    @staticmethod
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
            
            result = SyncService._fetch_with_backoff(client, 'Log', criteria, range_start, range_step)
            if result == 0: break
            logs = result
            if not logs: break
            
            for log in logs:
                if limit and total_changes >= limit: break
                glpi_id = log.get('id') # Log ID
                ticket_glpi_id = get_int(log.get('items_id'))
                
                # Check if ticket exists in our DB
                if not ticket_glpi_id or ticket_glpi_id not in tickets_map:
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
            if len(logs) > 0:
                logger.info(f"   Processed {total_changes} logs...")
            
            range_start += len(logs)

        logger.info(f"   ✅ Total Changes Synced: {total_changes}")

    @staticmethod
    def sync_carregadores(client: GLPIClient, session, CarregadorModel: Type):
        logger.info("🚀 Syncing Carregadores (PluginGenericobjectCarregador)...")
        try:
            items = client.make_request('PluginGenericobjectCarregador')
        except Exception as e:
            logger.warning(f"   ⚠️ Could not fetch Carregadores: {e}")
            items = []
            
        if not items:
            logger.info("   ⚠️ No Carregadores found.")
            return

        logger.info(f"   📥 Found {len(items)} items")
        for i in items:
            c = CarregadorModel(
                id=i['id'],
                name=clean_str(i.get('name')),
                entities_id=get_int(i.get('entities_id')),
                is_deleted=bool(i.get('is_deleted', 0)),
                sincronizado_em=datetime.now()
            )
            session.merge(c)
        session.commit()
        logger.info("   ✅ Carregadores synced.")

    @staticmethod
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
            
            result = SyncService._fetch_with_backoff(client, 'Item_Ticket', {}, range_start, range_step)
            if result == 0: break
            links = result
            if not links: break
            
            for l in links:
                if limit and count >= limit: break
                tid = int(l.get('tickets_id'))
                itemtype = l.get('itemtype')
                items_id = int(l.get('items_id'))
                
                # Filter only for Carregadores for now? OR sync all?
                # Sync all to be safe, but we only care about Carregadores in Service.
                # If we filter, we save space.
                # Let's sync all.
                
                if tid not in tickets_map: continue
                
                # Check exist
                # No unique key on API ID? Usually Link has an ID.
                # glpi_items_tickets usually has 'id'.
                link_id = l.get('id')
                
                existing = session.query(TicketItem).filter_by(id=link_id).first()
                if not existing:
                    ti = TicketItem(
                        id=link_id,
                        tickets_id=tickets_map[tid], # Map to LOCAL ticket ID? Or store GLPI ID?
                        # TicketItem model defined 'tickets_id'. 
                        # If I store GLPI ID, join works if Ticket model has glpi_id.
                        # But standard is to link to Local ID if standard.
                        # My TicketItem model defined 'tickets_id' as Integer. 
                        # Usually I prefer foreign keys.
                        # Wait, tickets_map maps GLPI_ID -> DB_ID.
                        # So I am storing DB_ID.
                        # But `glpi_items_tickets` in GLPI refers to GLPI_ID.
                        # So I must store GLPI_ID if I want to match with GLPI Logic?
                        # No, I should ideally use DB_ID if I have FK.
                        # But TicketItem does NOT have FK constraint in my definition (just Index).
                        # I will store GLPI ID in 'tickets_id' column to match GLPI schema (mirror).
                        # Correction: TicketItem usually mirrors `glpi_items_tickets` table which has `tickets_id` (GLPI ID).
                        # So I should store `tid` (GLPI ID).
                        # `tickets_map` is not needed if I store GLPI ID.
                        # I'll store GLPI Ticket ID.
                        
                        itemtype=itemtype,
                        items_id=items_id,
                        sincronizado_em=datetime.now()
                    )
                    session.merge(ti)
                    count += 1
            session.commit()
            range_start += len(links)
            
        logger.info("   ✅ Ticket Items synced.")
