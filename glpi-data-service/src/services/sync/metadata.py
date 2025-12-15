
import logging
from datetime import datetime
from typing import Type, Dict

from src.core.glpi_client import GLPIClient
from .utils import clean_str

logger = logging.getLogger(__name__)

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
