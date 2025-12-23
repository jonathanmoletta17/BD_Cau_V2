
import logging
from datetime import datetime
from typing import Type

from src.core.glpi_client import GLPIClient
from .utils import clean_str, get_int

logger = logging.getLogger(__name__)

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
