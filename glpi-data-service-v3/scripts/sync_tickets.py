"""
Tickets Synchronization Script for V3
Syncs tickets and their actors (users/groups) from GLPI to PostgreSQL
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
import hashlib
import html
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import config, Database, data_cleaning
from sqlalchemy import text
from src.core.glpi_client import GLPIClient
from src.modules.dtic.tickets import Ticket, TicketUser, TicketGroup, TicketChange
from src.modules.dtic.metadata import User, Group, Entity, ITILCategory, Location

# Import data cleaning functions from centralized module
clean_usuario_nome = data_cleaning.clean_usuario_nome
get_campo_name = data_cleaning.get_campo_name
treat_empty = data_cleaning.treat_empty_value
load_user_map = data_cleaning.load_user_lookup
FIELD_MAPPING = data_cleaning.FIELD_MAPPING

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_str(val):
    """Convert empty strings to None."""
    if isinstance(val, str) and not val.strip():
        return None
    return val


def get_int(val):
    """Safely convert value to int."""
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
    """Parse GLPI date string."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None


def calc_hash(t):
    """Calculate ticket hash for change detection."""
    hash_str = f"{t.get('name', '')}{t.get('content', '')}{t.get('status', '')}{t.get('priority', '')}"
    return hashlib.md5(hash_str.encode()).hexdigest()


def clean_html(raw_html):
    """Clean HTML from description."""
    if not raw_html:
        return None
    
    # Decode HTML entities
    decoded = html.unescape(str(raw_html))
    decoded = html.unescape(decoded)
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', decoded)
    text_content = " ".join(clean.split())
    
    return text_content if text_content else None


# Note: FIELD_MAPPING, clean_usuario_nome, get_campo_name, treat_empty, load_user_map
# are now imported from src.core.data_cleaning module (see imports at top of file)


def sync_tickets(client: GLPIClient, session, valid_ids):
    """Sync tickets from GLPI."""
    logger.info("🚀 Syncing Tickets...")
    
    range_start = 0
    range_step = 100
    total_processed = 0
    
    while True:
        range_header = f"{range_start}-{range_start + range_step - 1}"
        logger.info(f"   📥 Range: {range_header}")
        
        try:
            tickets = client.make_request('Ticket', {
                'range': range_header,
                'expand_dropdowns': 'false'
            })
        except Exception as e:
            if "RANGE_EXCEED" in str(e) or "400" in str(e):
                logger.info("   ✅ End of tickets list")
                break
            raise
        
        if not tickets:
            break
        
        for t in tickets:
            glpi_id = t.get('id')
            
            # Validate and resolve FKs
            entidade_id = get_int(t.get('entities_id'))
            if entidade_id and entidade_id not in valid_ids['entities']:
                entidade_id = None
            
            categoria_id = get_int(t.get('itilcategories_id'))
            if categoria_id and categoria_id not in valid_ids['categories']:
                categoria_id = None
            
            localizacao_id = get_int(t.get('locations_id'))
            if localizacao_id and localizacao_id not in valid_ids['locations']:
                localizacao_id = None
            
            ultimo_atualizador_id = get_int(t.get('users_id_lastupdater'))
            if ultimo_atualizador_id and ultimo_atualizador_id not in valid_ids['users']:
                ultimo_atualizador_id = None
            
            # Check if ticket exists
            existing = session.query(Ticket).filter_by(glpi_id=glpi_id).first()
            
            if existing:
                # Update existing
                existing.titulo = clean_str(t.get('name', ''))[:500] if t.get('name') else None
                existing.descricao = clean_html(t.get('content'))
                existing.status_id = get_int(t.get('status'))
                existing.prioridade_id = get_int(t.get('priority'))
                existing.tipo_id = get_int(t.get('type'))
                existing.impact = get_int(t.get('impact'))
                existing.urgency = get_int(t.get('urgency'))
                existing.categoria_id = categoria_id
                existing.entidade_id = entidade_id
                existing.localizacao_id = localizacao_id
                existing.ultimo_atualizador_id = ultimo_atualizador_id
                existing.tipo_requisicao_id = get_int(t.get('requesttypes_id'))
                existing.atualizado_em = parse_date(t.get('date_mod'))
                existing.solucionado_em = parse_date(t.get('solvedate'))
                existing.fechado_em = parse_date(t.get('closedate'))
                existing.tempo_para_resolver = get_int(t.get('time_to_resolve'))
                existing.tempo_para_atribuir = get_int(t.get('time_to_own'))
                existing.tempo_primeira_interacao = get_int(t.get('takeintoaccount_delay_stat'))
                existing.tempo_acao_total = get_int(t.get('actiontime'))
                existing.ticket_hash = calc_hash(t)
                existing.is_deleted = t.get('is_deleted') == 1
                existing.sincronizado_em = datetime.now()
            else:
                # Create new
                ticket = Ticket(
                    glpi_id=glpi_id,
                    titulo=clean_str(t.get('name', ''))[:500] if t.get('name') else None,
                    descricao=clean_html(t.get('content')),
                    status_id=get_int(t.get('status')),
                    prioridade_id=get_int(t.get('priority')),
                    tipo_id=get_int(t.get('type')),
                    impact=get_int(t.get('impact')),
                    urgency=get_int(t.get('urgency')),
                    categoria_id=categoria_id,
                    entidade_id=entidade_id,
                    localizacao_id=localizacao_id,
                    ultimo_atualizador_id=ultimo_atualizador_id,
                    tipo_requisicao_id=get_int(t.get('requesttypes_id')),
                    criado_em=parse_date(t.get('date')),
                    atualizado_em=parse_date(t.get('date_mod')),
                    solucionado_em=parse_date(t.get('solvedate')),
                    fechado_em=parse_date(t.get('closedate')),
                    tempo_para_resolver=get_int(t.get('time_to_resolve')),
                    tempo_para_atribuir=get_int(t.get('time_to_own')),
                    tempo_primeira_interacao=get_int(t.get('takeintoaccount_delay_stat')),
                    tempo_acao_total=get_int(t.get('actiontime')),
                    ticket_hash=calc_hash(t),
                    url=f"http://cau.ppiratini.intra.rs.gov.br/glpi/front/ticket.form.php?id={glpi_id}",
                    is_deleted=t.get('is_deleted') == 1,
                    sincronizado_em=datetime.now(),
                    versao=1
                )
                session.add(ticket)
        
        session.commit()
        total_processed += len(tickets)
        logger.info(f"   ✅ Processed {total_processed} tickets")
        range_start += range_step
    
    count = session.query(Ticket).count()
    logger.info(f"\n   🏁 Total tickets in DB: {count}\n")


def sync_ticket_actors(client: GLPIClient, session):
    """Sync ticket actors (users and groups)."""
    logger.info("[SYNC] Syncing Ticket Actors...")
    
    # Build ticket GLPI ID -> internal ID map
    ticket_map = {t.glpi_id: t.id for t in session.query(Ticket.glpi_id, Ticket.id).all()}
    logger.info(f"   [FETCH] {len(ticket_map)} tickets in database")
    
    # Get valid user and group IDs for FK validation
    valid_users = set(u.id for u in session.query(User.id).all())
    valid_groups = set(g.id for g in session.query(Group.id).all())
    logger.info(f"   [INFO] Valid users: {len(valid_users)}, Valid groups: {len(valid_groups)}")
    
    # Sync Ticket Users (all types: 1=Requester, 2=Assigned, 3=Observer)
    logger.info("\n   [USERS] Syncing Ticket-User relationships...")
    range_start = 0
    range_step = 2000
    total_users = 0
    skipped_users = 0
    
    while True:
        range_header = f"{range_start}-{range_start + range_step - 1}"
        
        try:
            actors = client.make_request('Ticket_User', {'range': range_header})
        except Exception as e:
            if "RANGE_EXCEED" in str(e) or "400" in str(e):
                break
            raise
        
        if not actors:
            break
        
        for a in actors:
            try:
                glpi_tid = int(a.get('tickets_id'))
                uid = int(a.get('users_id'))
                actor_type = int(a.get('type', 1))
                
                # Validate FK - skip if invalid
                if uid not in valid_users:
                    skipped_users += 1
                    continue
                
                if glpi_tid in ticket_map:
                    # Check if exists
                    existing = session.query(TicketUser).filter_by(
                        ticket_id=ticket_map[glpi_tid],
                        user_id=uid,
                        type=actor_type
                    ).first()
                    
                    if not existing:
                        ticket_user = TicketUser(
                            ticket_id=ticket_map[glpi_tid],
                            user_id=uid,
                            type=actor_type,
                            sincronizado_em=datetime.now()
                        )
                        session.add(ticket_user)
                        total_users += 1
            except (ValueError, TypeError):
                continue
        
        session.commit()
        logger.info(f"      Processed {range_start + len(actors)} records...")
        range_start += range_step
    
    logger.info(f"   [OK] {total_users} ticket-user relationships added")
    logger.info(f"   [INFO] Skipped {skipped_users} invalid user FKs\n")
    
    # Sync Ticket Groups
    logger.info("   [USERS] Syncing Ticket-Group relationships...")
    range_start = 0
    total_groups = 0
    skipped_groups = 0
    
    while True:
        range_header = f"{range_start}-{range_start + range_step - 1}"
        
        try:
            groups = client.make_request('Group_Ticket', {'range': range_header})
        except Exception as e:
            if "RANGE_EXCEED" in str(e) or "400" in str(e):
                break
            raise
        
        if not groups:
            break
        
        for g in groups:
            try:
                glpi_tid = int(g.get('tickets_id'))
                gid = int(g.get('groups_id'))
                group_type = int(g.get('type', 2))
                
                # Validate FK - skip if invalid
                if gid not in valid_groups:
                    skipped_groups += 1
                    continue
                
                if glpi_tid in ticket_map:
                    # Check if exists
                    existing = session.query(TicketGroup).filter_by(
                        ticket_id=ticket_map[glpi_tid],
                        group_id=gid,
                        type=group_type
                    ).first()
                    
                    if not existing:
                        ticket_group = TicketGroup(
                            ticket_id=ticket_map[glpi_tid],
                            group_id=gid,
                            type=group_type,
                            sincronizado_em=datetime.now()
                        )
                        session.add(ticket_group)
                        total_groups += 1
            except (ValueError, TypeError):
                continue
        
        session.commit()
        logger.info(f"      Processed {range_start + len(groups)} records...")
        range_start += range_step
    
    logger.info(f"   [OK] {total_groups} ticket-group relationships added")
    logger.info(f"   [INFO] Skipped {skipped_groups} invalid group FKs\n")


def sync_ticket_changes(client: GLPIClient, session):
    """Sync ticket changes (logs) - OPTIMIZED with SET-based duplicate detection."""
    logger.info("[SYNC] Syncing Ticket Changes (Logs)...")
    
    # Load user map for reverse lookup
    user_map = load_user_map(session)
    
    # Build ticket GLPI ID -> internal ID map
    ticket_map = {t.glpi_id: t.id for t in session.query(Ticket.glpi_id, Ticket.id).all()}
    logger.info(f"   [FETCH] {len(ticket_map)} tickets in database")
    
    # OPTIMIZATION: Load all existing glpi_ids into a SET (1 query instead of 4M queries)
    logger.info("   [FETCH] Loading existing change IDs into memory...")
    existing_ids = set(row.glpi_id for row in session.query(TicketChange.glpi_id).all())
    logger.info(f"   [FETCH] {len(existing_ids)} existing changes loaded")
    
    range_start = 0
    range_step = 2000
    total_changes = 0
    
    while True:
        range_header = f"{range_start}-{range_start + range_step - 1}"
        
        try:
            # Fetch Logs for Tickets
            logs = client.make_request('Log', {
                'range': range_header,
                'criteria[0][field]': 'itemtype',
                'criteria[0][searchtype]': 'equals',
                'criteria[0][value]': 'Ticket',
                'sort': 'id',
                'order': 'ASC'
            })
        except Exception as e:
            if "RANGE_EXCEED" in str(e) or "400" in str(e):
                break
            raise
        
        if not logs:
            break
        
        for l in logs:
            try:
                glpi_id = int(l.get('id'))
                glpi_tid = int(l.get('items_id'))
                
                if glpi_tid in ticket_map:
                    # OPTIMIZED: Check against in-memory SET (O(1) instead of DB query)
                    if glpi_id not in existing_ids:
                        # Prepare data
                        u_nome = clean_usuario_nome(l.get('user_name'))
                        u_id = get_int(l.get('users_id'))
                        
                        # Reverse lookup if ID is missing
                        if u_id is None and u_nome:
                            u_id = user_map.get(u_nome)
                            
                        change = TicketChange(
                            glpi_id=glpi_id,
                            ticket_id=ticket_map[glpi_tid],
                            data_mudanca=parse_date(l.get('date_mod')),
                            usuario_id=u_id,
                            usuario_nome=u_nome,
                            campo=get_campo_name(l.get('id_search_option')),
                            campo_id=get_int(l.get('id_search_option')),
                            valor_antigo=treat_empty(l.get('old_value')),
                            valor_novo=treat_empty(l.get('new_value')),
                            sincronizado_em=datetime.now()
                        )
                        session.add(change)
                        existing_ids.add(glpi_id)  # Add to set to prevent duplicates in same batch
                        total_changes += 1
            except (ValueError, TypeError):
                continue
        
        session.commit()
        logger.info(f"      Processed {range_start + len(logs)} logs...")
        range_start += range_step
    
    logger.info(f"   [OK] {total_changes} ticket changes added\n")


def main():
    """Main synchronization function."""
    print("=" * 70)
    print("GLPI TICKETS SYNCHRONIZATION (V3)")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        # Create session
        session = Database.get_session(context="dtic")
        
        # Load valid IDs for FK validation
        logger.info("📥 Loading valid IDs for FK validation...")
        valid_ids = {
            'entities': set(e.id for e in session.query(Entity.id).all()),
            'users': set(u.id for u in session.query(User.id).all()),
            'groups': set(g.id for g in session.query(Group.id).all()),
            'categories': set(c.id for c in session.query(ITILCategory.id).all()),
            'locations': set(l.id for l in session.query(Location.id).all())
        }
        logger.info(f"   ✅ Entities: {len(valid_ids['entities'])}, Users: {len(valid_ids['users'])}, "
                   f"Groups: {len(valid_ids['groups'])}, Categories: {len(valid_ids['categories'])}\n")
        
        # Create GLPI client
        with GLPIClient(
            config.GLPI_DTIC_URL,
            config.GLPI_DTIC_APP_TOKEN,
            config.GLPI_DTIC_USER_TOKEN
        ) as client:
            
            # Sync tickets
            sync_tickets(client, session, valid_ids)
            
            # Sync actors
            sync_ticket_actors(client, session)
            
            # Sync changes
            sync_ticket_changes(client, session)
        
        session.close()
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        print("=" * 70)
        print(f"[OK] TICKETS SYNC COMPLETED in {duration:.1f}s")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
