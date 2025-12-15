import json
import os
from typing import List, Dict
from src.services.glpi_client import GLPIClient
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

CATEGORIES_FILE = "categories_list.json"

class SyncService:
    def __init__(self, glpi_client: GLPIClient):
        self.glpi = glpi_client
        self.categories = self._load_categories()

    def _load_categories(self) -> List[Dict]:
        if os.path.exists(CATEGORIES_FILE):
            try:
                with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load categories file: {e}")
        return []

    def _save_categories(self, categories: List[Dict]):
        try:
            with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(categories, f, ensure_ascii=False, indent=2)
            self.categories = categories # Update in-memory
        except Exception as e:
            logger.error(f"Failed to save categories file: {e}")

    async def sync_categories(self):
        """
        Fetches categories from GLPI and saves the full taxonomy to a JSON file.
        No embeddings or vector search required anymore.
        """
        logger.info("Starting category synchronization (Full Context Mode)...")
        
        try:
            # 1. Fetch from source
            raw_cats = await self.glpi.get_all_categories()
            
            # 2. Process (just format them nicely if needed, or store raw)
            # We prefer storing a clean list for the classifier to read
            clean_cats = []
            for item in raw_cats:
                clean_cats.append({
                    "id": item['id'],
                    "name": item['name'],
                    "completename": item['completename'],
                    "comment": item.get('comment', ''),
                    "level": item.get('level', 1)
                })

            # 3. Save to file
            self._save_categories(clean_cats)
            
            logger.info(f"Sync complete. Total Categories: {len(clean_cats)}")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
