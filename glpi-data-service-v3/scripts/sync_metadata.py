"""
Metadata Synchronization Script for V3
Syncs all metadata entities from GLPI to PostgreSQL
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import config, Database
from src.core.glpi_client import GLPIClient
from src.modules.dtic.metadata import (
    User, Group, Entity, ITILCategory, Location, Profile,
    GroupUser, ProfileUser
)

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


def sync_entities(client: GLPIClient, session):
    """Sync entities from GLPI."""
    logger.info("🚀 Syncing Entities...")
    
    entities = client.get_entities()
    logger.info(f"   📥 Found {len(entities)} entities in GLPI")
    
    for ent in entities:
        entity = Entity(
            id=ent['id'],
            name=clean_str(ent.get('name')),
            completename=clean_str(ent.get('completename')),
            level=ent.get('level'),
            entities_id=ent.get('entities_id') if ent.get('entities_id') != 0 else None,
            sincronizado_em=datetime.now()
        )
        session.merge(entity)  # Upsert
    
    session.commit()
    count = session.query(Entity).count()
    logger.info(f"   ✅ {count} entities in database\n")


def sync_locations(client: GLPIClient, session):
    """Sync locations from GLPI."""
    logger.info("🚀 Syncing Locations...")
    
    locations = client.get_locations()
    logger.info(f"   📥 Found {len(locations)} locations in GLPI")
    
    for loc in locations:
        location = Location(
            id=loc['id'],
            name=clean_str(loc.get('completename') or loc.get('name')),
            level=loc.get('level'),
            parent_id=loc.get('locations_id') if loc.get('locations_id') != 0 else None,
            ancestors_cache=clean_str(loc.get('ancestors_cache')),
            sincronizado_em=datetime.now()
        )
        session.merge(location)
    
    session.commit()
    count = session.query(Location).count()
    logger.info(f"   ✅ {count} locations in database\n")


def sync_groups(client: GLPIClient, session):
    """Sync groups from GLPI."""
    logger.info("🚀 Syncing Groups...")
    
    groups = client.get_groups()
    logger.info(f"   📥 Found {len(groups)} groups in GLPI")
    
    for grp in groups:
        group = Group(
            id=grp['id'],
            name=clean_str(grp.get('name')),
            is_task=bool(grp.get('is_task', 0)),
            is_itemgroup=bool(grp.get('is_itemgroup', 0)),
            sincronizado_em=datetime.now()
        )
        session.merge(group)
    
    session.commit()
    count = session.query(Group).count()
    logger.info(f"   ✅ {count} groups in database\n")


def sync_users(client: GLPIClient, session):
    """Sync users from GLPI (including emails)."""
    logger.info("🚀 Syncing Users...")
    
    users = client.get_users()
    logger.info(f"   📥 Found {len(users)} users in GLPI")
    
    # Fetch user emails separately
    logger.info("   📧 Fetching user emails...")
    try:
        user_emails = client.get_all_pages('UserEmail')
        email_map = {ue.get('users_id'): ue.get('email') for ue in user_emails if ue.get('users_id') and ue.get('email')}
        logger.info(f"   📧 Mapped {len(email_map)} emails")
    except:
        email_map = {}
    
    for usr in users:
        uid = usr['id']
        email = usr.get('email') or email_map.get(uid)
        
        user = User(
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
    count = session.query(User).count()
    logger.info(f"   ✅ {count} users in database\n")


def sync_categories(client: GLPIClient, session):
    """Sync ITIL categories from GLPI."""
    logger.info("🚀 Syncing Categories...")
    
    categories = client.get_itil_categories()
    logger.info(f"   📥 Found {len(categories)} categories in GLPI")
    
    for cat in categories:
        category = ITILCategory(
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
    count = session.query(ITILCategory).count()
    logger.info(f"   ✅ {count} categories in database\n")


def sync_profiles(client: GLPIClient, session):
    """Sync profiles from GLPI."""
    logger.info("🚀 Syncing Profiles...")
    
    profiles = client.get_profiles()
    logger.info(f"   📥 Found {len(profiles)} profiles in GLPI")
    
    for prof in profiles:
        profile = Profile(
            id=prof['id'],
            name=clean_str(prof.get('name')),
            is_default=bool(prof.get('is_default', 0)),
            sincronizado_em=datetime.now()
        )
        session.merge(profile)
    
    session.commit()
    count = session.query(Profile).count()
    logger.info(f"   ✅ {count} profiles in database\n")


def sync_groups_users(client: GLPIClient, session):
    """Sync group-user relationships from GLPI."""
    logger.info("🚀 Syncing Groups-Users relationships...")
    
    # Get valid IDs for validation
    valid_users = set(u.id for u in session.query(User.id).all())
    valid_groups = set(g.id for g in session.query(Group.id).all())
    logger.info(f"   📥 Valid IDs: {len(valid_users)} users, {len(valid_groups)} groups")
    
    relationships = client.get_groups_users()
    logger.info(f"   📥 Found {len(relationships)} relationships in GLPI")
    
    inserted = 0
    skipped = 0
    
    for rel in relationships:
        user_id = rel.get('users_id')
        group_id = rel.get('groups_id')
        
        # Validate FK
        if user_id not in valid_users or group_id not in valid_groups:
            skipped += 1
            continue
        
        # Check if exists (query by unique constraint fields)
        existing = session.query(GroupUser).filter_by(
            users_id=user_id,
            groups_id=group_id
        ).first()
        
        if existing:
            # Update existing
            existing.is_dynamic = bool(rel.get('is_dynamic', 0))
            existing.is_manager = bool(rel.get('is_manager', 0))
            existing.sincronizado_em = datetime.now()
        else:
            # Insert new
            group_user = GroupUser(
                users_id=user_id,
                groups_id=group_id,
                is_dynamic=bool(rel.get('is_dynamic', 0)),
                is_manager=bool(rel.get('is_manager', 0)),
                sincronizado_em=datetime.now()
            )
            session.add(group_user)
        inserted += 1
    
    session.commit()
    count = session.query(GroupUser).count()
    logger.info(f"   ✅ {count} relationships in database")
    logger.info(f"   ℹ️  Processed: {inserted}, Skipped (invalid FK): {skipped}\n")


def sync_profiles_users(client: GLPIClient, session):
    """Sync profile-user relationships from GLPI."""
    logger.info("🚀 Syncing Profiles-Users relationships...")
    
    # Get valid IDs
    valid_users = set(u.id for u in session.query(User.id).all())
    valid_profiles = set(p.id for p in session.query(Profile.id).all())
    valid_entities = set(e.id for e in session.query(Entity.id).all())
    logger.info(f"   📥 Valid IDs: {len(valid_users)} users, {len(valid_profiles)} profiles, {len(valid_entities)} entities")
    
    relationships = client.get_profiles_users()
    logger.info(f"   📥 Found {len(relationships)} relationships in GLPI")
    
    inserted = 0
    skipped = 0
    
    for rel in relationships:
        user_id = rel.get('users_id')
        profile_id = rel.get('profiles_id')
        entity_id = rel.get('entities_id')
        
        # Validate FK
        if (user_id not in valid_users or 
            profile_id not in valid_profiles or 
            entity_id not in valid_entities):
            skipped += 1
            continue
        
        # Check if exists
        existing = session.query(ProfileUser).filter_by(
            users_id=user_id,
            profiles_id=profile_id,
            entities_id=entity_id
        ).first()
        
        if existing:
            # Update existing
            existing.is_recursive = bool(rel.get('is_recursive', 0))
            existing.is_dynamic = bool(rel.get('is_dynamic', 0))
            existing.sincronizado_em = datetime.now()
        else:
            # Insert new
            profile_user = ProfileUser(
                users_id=user_id,
                profiles_id=profile_id,
                entities_id=entity_id,
                is_recursive=bool(rel.get('is_recursive', 0)),
                is_dynamic=bool(rel.get('is_dynamic', 0)),
                sincronizado_em=datetime.now()
            )
            session.add(profile_user)
        inserted += 1
    
    session.commit()
    count = session.query(ProfileUser).count()
    logger.info(f"   ✅ {count} relationships in database")
    logger.info(f"   ℹ️  Processed: {inserted}, Skipped (invalid FK): {skipped}\n")


def main():
    """Main synchronization function."""
    print("=" * 70)
    print("GLPI METADATA SYNCHRONIZATION (V3)")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        # Create session
        session = Database.get_session(context="dtic")
        
        # Create GLPI client
        with GLPIClient(
            config.GLPI_DTIC_URL,
            config.GLPI_DTIC_APP_TOKEN,
            config.GLPI_DTIC_USER_TOKEN
        ) as client:
            
            # Sync in dependency order
            sync_entities(client, session)
            sync_locations(client, session)
            sync_groups(client, session)
            sync_users(client, session)
            sync_categories(client, session)
            sync_profiles(client, session)
            sync_groups_users(client, session)
            sync_profiles_users(client, session)
        
        session.close()
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        print("=" * 70)
        print(f"[OK] METADATA SYNC COMPLETED in {duration:.1f}s")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
