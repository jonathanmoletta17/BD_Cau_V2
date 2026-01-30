"""
GLPI Data Service - Database Validation Script
Checks for duplicates and data consistency in DTIC and SIS schemas.
"""
import sys
import logging
from pathlib import Path
from sqlalchemy import text, func

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database
# Import models to ensure they are registered
import src.modules.dtic.metadata.models as dtic_meta
import src.modules.dtic.tickets.models as dtic_tickets
import src.modules.sis.metadata.models as sis_meta
import src.modules.sis.tickets.models as sis_tickets

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - VALIDATION - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_duplicates(session, context, model, constraint_cols):
    """Check for duplicates based on a specific constraint."""
    cols = [getattr(model, col) for col in constraint_cols]
    query = session.query(*cols, func.count('*').label('count'))\
        .group_by(*cols)\
        .having(func.count('*') > 1)
    
    dupes = query.all()
    if dupes:
        logger.error(f"❌ [{context.upper()}] Found {len(dupes)} duplicates in {model.__tablename__} on {constraint_cols}!")
        for d in dupes[:5]:
            logger.error(f"   - {d}")
        return False
    return True

def validate_context(context):
    logger.info(f"\n🔍 Validating Context: {context.upper()}...")
    session = Database.get_session(context=context)
    try:
        if context == 'dtic':
            models = {
                'User': (dtic_meta.User, ['id']),
                'Group': (dtic_meta.Group, ['id']),
                'Entity': (dtic_meta.Entity, ['id']),
                'Ticket': (dtic_tickets.Ticket, ['glpi_id']),
            }
        else:
            models = {
                'User': (sis_meta.User, ['id']),
                'Group': (sis_meta.Group, ['id']),
                'Entity': (sis_meta.Entity, ['id']),
                'Ticket': (sis_tickets.Ticket, ['glpi_id']),
            }

        all_valid = True
        
        # 1. Count Records
        for name, (model, cols) in models.items():
            count = session.query(model).count()
            logger.info(f"   📊 {name}: {count} records")
            
            # 2. Check Duplicates
            if not check_duplicates(session, context, model, cols):
                all_valid = False
            else:
                logger.info(f"   ✅ {name}: No duplicates on {cols}")

        return all_valid

    except Exception as e:
        logger.error(f"❌ Error validating {context}: {e}")
        return False
    finally:
        session.close()

def main():
    logger.info("🚀 Starting Database Validation...")
    
    dtic_ok = validate_context('dtic')
    sis_ok = validate_context('sis')
    
    if dtic_ok and sis_ok:
        logger.info("\n✅ ALL CHECKS PASSED. Database is clean.")
        sys.exit(0)
    else:
        logger.error("\n❌ ISSUES FOUND. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
