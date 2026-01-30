
import logging
from datetime import datetime
from typing import Type, Dict

from src.core.glpi_client import GLPIClient
from .utils import clean_str, parse_date
from .core import fetch_with_backoff

logger = logging.getLogger(__name__)

def _fetch_all(client: GLPIClient, entity_type: str, criteria: Dict):
    start = 0
    step = 1000
    items = []
    while True:
        result = fetch_with_backoff(client, entity_type, criteria, start, step)
        if result == 0 or not result:
            break
        items.extend(result)
        start += len(result)
    return items

def _since_criteria(since_date: datetime = None) -> Dict:
    criteria = {}
    if since_date:
        criteria['criteria[0][field]'] = 'date_mod'
        criteria['criteria[0][searchtype]'] = 'morethan'
        criteria['criteria[0][value]'] = since_date.strftime('%Y-%m-%d %H:%M:%S')
    return criteria

def sync_entities(client: GLPIClient, session, EntityModel: Type, since_date: datetime = None):
    logger.info("🚀 Syncing Entities...")
    criteria = _since_criteria(since_date)
    entities = _fetch_all(client, 'Entity', criteria)
    logger.info(f"   📥 Found {len(entities)} entities")
    max_date_mod = None
    for ent in entities:
        date_mod = parse_date(ent.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
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
    session.expunge_all()
    logger.info(f"   ✅ Entities synced.")
    return max_date_mod

def sync_locations(client: GLPIClient, session, LocationModel: Type, since_date: datetime = None):
    logger.info("🚀 Syncing Locations...")
    criteria = _since_criteria(since_date)
    locations = _fetch_all(client, 'Location', criteria)
    logger.info(f"   📥 Found {len(locations)} locations")
    max_date_mod = None
    for loc in locations:
        date_mod = parse_date(loc.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
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
    session.expunge_all()
    logger.info(f"   ✅ Locations synced.")
    return max_date_mod

def sync_groups(client: GLPIClient, session, GroupModel: Type, since_date: datetime = None):
    logger.info("🚀 Syncing Groups...")
    criteria = _since_criteria(since_date)
    groups = _fetch_all(client, 'Group', criteria)
    logger.info(f"   📥 Found {len(groups)} groups")
    max_date_mod = None
    for grp in groups:
        date_mod = parse_date(grp.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
        group = GroupModel(
            id=grp['id'],
            name=clean_str(grp.get('name')),
            is_task=bool(grp.get('is_task', 0)),
            is_itemgroup=bool(grp.get('is_itemgroup', 0)),
            sincronizado_em=datetime.now()
        )
        session.merge(group)
    session.commit()
    session.expunge_all()
    logger.info(f"   ✅ Groups synced.")
    return max_date_mod

def sync_users(client: GLPIClient, session, UserModel: Type, since_date: datetime = None):
    logger.info("🚀 Syncing Users...")
    criteria = _since_criteria(since_date)
    users = _fetch_all(client, 'User', criteria)
    logger.info(f"   📥 Found {len(users)} users")
    # Emails
    try:
        logger.info("   📧 Fetching emails...")
        user_emails = client.get_all_pages('UserEmail')
        email_map = {ue.get('users_id'): ue.get('email') for ue in user_emails if ue.get('users_id')}
    except:
        email_map = {}
    
    max_date_mod = None
    for usr in users:
        date_mod = parse_date(usr.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
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
    session.expunge_all()
    logger.info(f"   ✅ Users synced.")
    return max_date_mod

def sync_categories(client: GLPIClient, session, CategoryModel: Type, since_date: datetime = None):
    logger.info("🚀 Syncing Categories...")
    criteria = _since_criteria(since_date)
    categories = _fetch_all(client, 'ITILCategory', criteria)
    logger.info(f"   📥 Found {len(categories)} categories")
    max_date_mod = None
    for cat in categories:
        date_mod = parse_date(cat.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
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
    session.expunge_all()
    logger.info("   ✅ Categories synced.")
    return max_date_mod

def sync_profiles(client: GLPIClient, session, ProfileModel: Type, since_date: datetime = None):
    logger.info("🚀 Syncing Profiles...")
    criteria = _since_criteria(since_date)
    profiles = _fetch_all(client, 'Profile', criteria)
    logger.info(f"   📥 Found {len(profiles)} profiles")
    max_date_mod = None
    for prof in profiles:
        date_mod = parse_date(prof.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
        profile = ProfileModel(
            id=prof['id'],
            name=clean_str(prof.get('name')),
            is_default=bool(prof.get('is_default', 0)),
            sincronizado_em=datetime.now()
        )
        session.merge(profile)
    session.commit()
    session.expunge_all()
    logger.info("   ✅ Profiles synced.")
    return max_date_mod

def sync_groups_users(client: GLPIClient, session, GroupUserModel: Type, valid_ids: Dict, since_date: datetime = None):
    logger.info("🚀 Syncing Group-User Relations...")
    criteria = _since_criteria(since_date)
    relationships = _fetch_all(client, 'Group_User', criteria)
    logger.info(f"   📥 Found {len(relationships)} relations")
    
    valid_u = valid_ids['users']
    valid_g = valid_ids['groups']
    max_date_mod = None
    
    for rel in relationships:
        uid = rel.get('users_id')
        gid = rel.get('groups_id')
        if uid not in valid_u or gid not in valid_g:
            continue
        date_mod = parse_date(rel.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
        
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
    return max_date_mod

def sync_profiles_users(client: GLPIClient, session, ProfileUserModel: Type, valid_ids: Dict, since_date: datetime = None):
    logger.info("🚀 Syncing Profile-User Relations...")
    criteria = _since_criteria(since_date)
    relationships = _fetch_all(client, 'Profile_User', criteria)
    logger.info(f"   📥 Found {len(relationships)} relations")
    
    valid_u = valid_ids['users']
    valid_p = valid_ids['profiles']
    valid_e = valid_ids['entities']
    
    seen = set()
    max_date_mod = None
    for rel in relationships:
        uid = rel.get('users_id')
        pid = rel.get('profiles_id')
        eid = rel.get('entities_id')
        
        if uid not in valid_u or pid not in valid_p or eid not in valid_e:
            continue
        date_mod = parse_date(rel.get('date_mod'))
        if date_mod and (not max_date_mod or date_mod > max_date_mod):
            max_date_mod = date_mod
            
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
    return max_date_mod
