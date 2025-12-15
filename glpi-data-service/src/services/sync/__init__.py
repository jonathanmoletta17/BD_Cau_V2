
"""
GLPI Sync Service Facade
Maintains backward compatibility by exposing split modules as a single class.
"""
from typing import Type, Dict, Any, List
from datetime import datetime
from src.core.glpi_client import GLPIClient

# Import sub-modules
from .core import fetch_with_backoff 
from .metadata import (
    sync_entities,
    sync_locations,
    sync_groups,
    sync_users,
    sync_categories,
    sync_profiles,
    sync_groups_users,
    sync_profiles_users
)
from .tickets import (
    sync_tickets,
    sync_ticket_actors,
    sync_ticket_items
)
from .changes import sync_ticket_changes
from .loaders import sync_carregadores

class SyncService:
    """Service to handle GLPI synchronization logic (Facade)."""
    
    # Core
    @staticmethod
    def _fetch_with_backoff(client: GLPIClient, entity_type: str, criteria: Dict[str, Any], 
                          start: int, step: int, limit_step: int = 1) -> Any:
        # Redirect to the function in core.py
        return fetch_with_backoff(client, entity_type, criteria, start, step, limit_step)

    # Metadata
    sync_entities = staticmethod(sync_entities)
    sync_locations = staticmethod(sync_locations)
    sync_groups = staticmethod(sync_groups)
    sync_users = staticmethod(sync_users)
    sync_categories = staticmethod(sync_categories)
    sync_profiles = staticmethod(sync_profiles)
    sync_groups_users = staticmethod(sync_groups_users)
    sync_profiles_users = staticmethod(sync_profiles_users)

    # Tickets
    sync_tickets = staticmethod(sync_tickets)
    sync_ticket_actors = staticmethod(sync_ticket_actors)
    sync_ticket_items = staticmethod(sync_ticket_items)
    
    # Changes
    sync_ticket_changes = staticmethod(sync_ticket_changes)
    
    # Loaders
    sync_carregadores = staticmethod(sync_carregadores)
