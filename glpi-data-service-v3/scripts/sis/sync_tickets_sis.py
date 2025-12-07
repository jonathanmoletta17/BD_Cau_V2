"""
SIS Tickets Synchronization - PIRATINI Context
Syncs all tickets from GLPI_SIS to PostgreSQL (sis schema)
Note: All tickets in SIS are from PIRATINI hierarchy (entity 1 and children)
"""
import sys
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from html import unescape
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config, Database
from src.core.glpi_client import GLPIClient
from src.modules.sis.tickets import Ticket

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Entity filter - PIRATINI
ENTITY_ID = 1


def clean_str(val):
    """Convert empty strings to None."""
    if isinstance(val, str) and not val.strip():
        return None
    return val


def get_int(val):
    """Safe int conversion."""
    if val is None or val == '':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def parse_date(date_str):
    """Parse GLPI date format."""
    if not date_str or date_str == 'NULL':
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None


def clean_html(html_text):
    """Remove HTML tags from text."""
    if not html_text:
        return None
    # Unescape HTML entities
    text = unescape(html_text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean whitespace
    text = ' '.join(text.split())
    return clean_str(text)


def calc_hash(ticket_data):
    """Calculate MD5 hash of ticket data."""
    hash_str = f"{ticket_data.get('name', '')}{ticket_data.get('content', '')}{ticket_data.get('date_mod', '')}"
    return hashlib.md5(hash_str.encode()).hexdigest()


def sync_tickets_batch(client, session, valid_ids, start=0, limit=100):
    """Sync a batch of tickets (filter by entity locally)."""
    logger.info(f"  📥 Fetching tickets {start}-{start+limit-1}...")
    
    # Fetch tickets from API (no filter - API doesn't support entity filter reliably)
    params = {
        'range': f'{start}-{start+limit-1}'
    }
    
    tickets_data = client.make_request('Ticket', params)
    
    if not tickets_data:
        logger.info(f"  ✓ No more tickets found")
        return 0
    
    logger.info(f"  📋 Processing {len(tickets_data)} tickets (filtering by entity_id={ENTITY_ID})...")
    
    inserted = 0
    updated = 0
    
    for tkt in tickets_data:
        glpi_id = tkt.get('id')
        entity_id = get_int(tkt.get('entities_id'))
        
        # Note: All tickets in SIS API are from PIRATINI hierarchy
        # No need to filter by entity
        
        # Validate foreign keys
        categoria_id = get_int(tkt.get('itilcategories_id'))
        if categoria_id and categoria_id not in valid_ids['categories']:
            categoria_id = None
        
        localizacao_id = get_int(tkt.get('locations_id'))
        if localizacao_id and localizacao_id not in valid_ids['locations']:
            localizacao_id = None
        
        # Create ticket object
        ticket = Ticket(
            glpi_id=glpi_id,
            titulo=clean_str(tkt.get('name')),
            descricao=clean_html(tkt.get('content')),
            status_id=get_int(tkt.get('status')),
            prioridade_id=get_int(tkt.get('priority')),
            tipo_id=get_int(tkt.get('type')),
            impact=get_int(tkt.get('impact')),
            urgency=get_int(tkt.get('urgency')),
            categoria_id=categoria_id,
            entidade_id=entity_id,
            localizacao_id=localizacao_id,
            tipo_requisicao_id=get_int(tkt.get('requesttypes_id')),
            criado_em=parse_date(tkt.get('date_creation')) or parse_date(tkt.get('date')),
            atualizado_em=parse_date(tkt.get('date_mod')),
            solucionado_em=parse_date(tkt.get('solvedate')),
            fechado_em=parse_date(tkt.get('closedate')),
            ticket_hash=calc_hash(tkt)
        )
        
        # Check if exists
        existing = session.query(Ticket).filter_by(glpi_id=glpi_id).first()
        
        if existing:
            # Update if hash changed
            if existing.ticket_hash != ticket.ticket_hash:
                session.merge(ticket)
                updated += 1
        else:
            session.add(ticket)
            inserted += 1
    
    session.commit()
    
    logger.info(f"  ✓ Batch processed: {inserted} inserted, {updated} updated")
    
    return len(tickets_data)


def get_valid_ids(session):
    """Get valid IDs for foreign key validation."""
    from src.modules.sis.metadata import Entity, ITILCategory, Location
    
    return {
        'entities': set([e.id for e in session.query(Entity.id).all()]),
        'categories': set([c.id for c in session.query(ITILCategory.id).all()]),
        'locations': set([l.id for l in session.query(Location.id).all()])
    }


def main(test_mode=False, test_limit=100):
    """Main synchronization function."""
    print("=" * 70)
    print("GLPI_SIS TICKETS SYNCHRONIZATION")
    print(f"Entity Filter: ID={ENTITY_ID} (PIRATINI)")
    if test_mode:
        print(f"Mode: TEST (limit={test_limit})")
    else:
        print("Mode: FULL")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        # Create session
        session = Database.get_session(context="sis")
        
        # Get valid IDs for FK validation
        logger.info("Loading valid IDs for FK validation...")
        valid_ids = get_valid_ids(session)
        logger.info(f"  ✓ {len(valid_ids['entities'])} entities, {len(valid_ids['categories'])} categories")
        
        # Create GLPI client
        with GLPIClient(
            config.GLPI_SIS_URL,
            config.GLPI_SIS_APP_TOKEN,
            config.GLPI_SIS_USER_TOKEN
        ) as client:
            
            # Sync in batches
            start = 0
            batch_size = 100
            total = 0
            
            max_tickets = test_limit if test_mode else 10000  # Safety limit
            
            while start < max_tickets:
                count = sync_tickets_batch(client, session, valid_ids, start, batch_size)
                
                if count == 0:
                    break
                
                total += count
                start += batch_size
                
                if test_mode and total >= test_limit:
                    logger.info(f"  ℹ️  Test limit reached ({test_limit})")
                    break
        
        session.close()
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        final_count = Database.get_session(context="sis").query(Ticket).count()
        
        print("\n" + "=" * 70)
        print(f"[OK] TICKETS SYNC COMPLETED in {duration:.1f}s")
        print(f"Total tickets in database: {final_count}")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Full sync mode
    main(test_mode=False)
