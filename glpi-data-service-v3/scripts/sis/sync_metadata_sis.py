"""
SIS Metadata Synchronization Script
Syncs metadata from GLPI_SIS to PostgreSQL (sis schema)
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config, Database
from src.core.glpi_client import GLPIClient
from src.modules.sis.metadata import (
    Entity, Group, ITILCategory, Location,
    User, Profile, ProfileUser, GroupUser
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


def sync_entities(client, session):
    """Sync entities from GLPI_SIS."""
    logger.info("🚀 Syncing Entities...")
    
    entities = client.get_entities()
    logger.info(f"   📥 Found {len(entities)} entities")
    
    for ent in entities:
        entity = Entity(
            id=ent['id'],
            name=clean_str(ent.get('name')),
            completename=clean_str(ent.get('completename')),
            level=ent.get('level'),
            entities_id=ent.get('entities_id') if ent.get('entities_id') != 0 else None
        )
        session.merge(entity)
    
    session.commit()
    count = session.query(Entity).count()
    logger.info(f"   ✅ {count} entities in sis schema\n")


def sync_groups(client, session):
    """Sync groups from GLPI_SIS."""
    logger.info("🚀 Syncing Groups...")
    
    groups = client.get_groups()
    logger.info(f"   📥 Found {len(groups)} groups")
    
    for grp in groups:
        group = Group(
            id=grp['id'],
            name=clean_str(grp.get('name')),
            is_task=bool(grp.get('is_task', 0)),
            is_itemgroup=bool(grp.get('is_itemgroup', 0))
        )
        session.merge(group)
    
    session.commit()
    count = session.query(Group).count()
    logger.info(f"   ✅ {count} groups in sis schema\n")


def sync_categories(client, session):
    """Sync ITIL categories from GLPI_SIS."""
    logger.info("🚀 Syncing Categories...")
    
    categories = client.get_itil_categories()
    logger.info(f"   📥 Found {len(categories)} categories")
    
    for cat in categories:
        category = ITILCategory(
            id=cat['id'],
            name=clean_str(cat.get('name')),
            completename=clean_str(cat.get('completename')),
            level=cat.get('level'),
            parent_id=cat.get('itilcategories_id'),
            ancestors_cache=clean_str(cat.get('ancestors_cache'))
        )
        session.merge(category)
    
    session.commit()
    count = session.query(ITILCategory).count()
    logger.info(f"   ✅ {count} categories in sis schema\n")


def sync_locations(client, session):
    """Sync locations from GLPI_SIS."""
    logger.info("🚀 Syncing Locations...")
    
    locations = client.get_locations()
    logger.info(f"   📥 Found {len(locations)} locations")
    
    for loc in locations:
        location = Location(
            id=loc['id'],
            name=clean_str(loc.get('completename') or loc.get('name')),
            level=loc.get('level'),
            parent_id=loc.get('locations_id') if loc.get('locations_id') != 0 else None,
            ancestors_cache=clean_str(loc.get('ancestors_cache'))
        )
        session.merge(location)
    
    session.commit()
    count = session.query(Location).count()
    logger.info(f"   ✅ {count} locations in sis schema\n")


def sync_users(client, session):
    """Sync users from GLPI_SIS."""
    logger.info("🚀 Syncing Users...")
    
    try:
        users = client.make_request('User')
        logger.info(f"   📥 Found {len(users)} users")
        
        for usr in users:
            user = User(
                id=usr['id'],
                name=clean_str(usr.get('name')),
                realname=clean_str(usr.get('realname')),
                firstname=clean_str(usr.get('firstname')),
                email=clean_str(usr.get('email')),
                is_active=bool(usr.get('is_active', 1)),
                is_deleted=bool(usr.get('is_deleted', 0))
            )
            session.merge(user)
        
        session.commit()
        count = session.query(User).count()
        logger.info(f"   ✅ {count} users in sis schema\n")
    except Exception as e:
        logger.warning(f"   ⚠ Could not sync users from API: {e}")
        logger.info("   ℹ️  Will extract users from ticket relationships later\n")


def sync_profiles(client, session):
    """Sync profiles from GLPI_SIS."""
    logger.info("🚀 Syncing Profiles...")
    
    try:
        profiles = client.make_request('Profile')
        logger.info(f"   📥 Found {len(profiles)} profiles")
        
        for prof in profiles:
            profile = Profile(
                id=prof['id'],
                name=clean_str(prof.get('name')),
                is_default=bool(prof.get('is_default', 0))
            )
            session.merge(profile)
        
        session.commit()
        count = session.query(Profile).count()
        logger.info(f"   ✅ {count} profiles in sis schema\n")
    except Exception as e:
        logger.warning(f"   ⚠ Could not sync profiles: {e}\n")


def sync_profile_users(client, session):
    """Sync profile-user relationships."""
    logger.info("🚀 Syncing Profile-User relationships...")
    
    try:
        # Get valid IDs
        valid_users = set([u.id for u in session.query(User.id).all()])
        valid_profiles = set([p.id for p in session.query(Profile.id).all()])
        valid_entities = set([e.id for e in session.query(Entity.id).all()])
        
        relations = client.make_request('Profile_User')
        logger.info(f"   📥 Found {len(relations)} relationships")
        
        inserted = 0
        skipped = 0
        
        for rel in relations:
            user_id = rel.get('users_id')
            profile_id = rel.get('profiles_id')
            entity_id = rel.get('entities_id')
            
            # Validate FKs
            if user_id not in valid_users:
                skipped += 1
                continue
            if profile_id not in valid_profiles:
                skipped += 1
                continue
            if entity_id and entity_id not in valid_entities:
                entity_id = None
            
            profile_user = ProfileUser(
                users_id=user_id,
                profiles_id=profile_id,
                entities_id=entity_id or 0,
                is_recursive=bool(rel.get('is_recursive', 0)),
                is_dynamic=bool(rel.get('is_dynamic', 0))
            )
            session.merge(profile_user)
            inserted += 1
        
        session.commit()
        count = session.query(ProfileUser).count()
        logger.info(f"   ✅ {count} profile-user relations ({inserted} new, {skipped} skipped)\n")
    except Exception as e:
        logger.warning(f"   ⚠ Could not sync profile-user relations: {e}\n")


def sync_group_users(client, session):
    """Sync group-user relationships."""
    logger.info("🚀 Syncing Group-User relationships...")
    
    try:
        # Get valid IDs
        valid_users = set([u.id for u in session.query(User.id).all()])
        valid_groups = set([g.id for g in session.query(Group.id).all()])
        
        relations = client.make_request('Group_User')
        logger.info(f"   📥 Found {len(relations)} relationships")
        
        inserted = 0
        skipped = 0
        
        for rel in relations:
            user_id = rel.get('users_id')
            group_id = rel.get('groups_id')
            
            # Validate FKs
            if user_id not in valid_users:
                skipped += 1
                continue
            if group_id not in valid_groups:
                skipped += 1
                continue
            
            group_user = GroupUser(
                users_id=user_id,
                groups_id=group_id,
                is_dynamic=bool(rel.get('is_dynamic', 0)),
                is_manager=bool(rel.get('is_manager', 0))
            )
            session.merge(group_user)
            inserted += 1
        
        session.commit()
        count = session.query(GroupUser).count()
        logger.info(f"   ✅ {count} group-user relations ({inserted} new, {skipped} skipped)\n")
    except Exception as e:
        logger.warning(f"   ⚠ Could not sync group-user relations: {e}\n")


def main():

    """Main synchronization function."""
    print("=" * 70)
    print("GLPI_SIS METADATA SYNCHRONIZATION")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        # Create session for SIS schema
        session = Database.get_session(context="sis")
        
        # Create GLPI client with SIS credentials
        with GLPIClient(
            config.GLPI_SIS_URL,
            config.GLPI_SIS_APP_TOKEN,
            config.GLPI_SIS_USER_TOKEN
        ) as client:
            
            # Sync in dependency order
            # Level 0: Independent entities
            sync_entities(client, session)
            sync_locations(client, session)
            sync_groups(client, session)
            sync_categories(client, session)
            
            # Level 0: Users and Profiles
            sync_users(client, session)
            sync_profiles(client, session)
            
            # Level 1: Relationships
            sync_profile_users(client, session)
            sync_group_users(client, session)
        
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
