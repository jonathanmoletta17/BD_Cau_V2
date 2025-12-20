
import requests
import logging
from typing import Dict, Any
from src.core.glpi_client import GLPIClient

logger = logging.getLogger(__name__)

def fetch_with_backoff(client: GLPIClient, entity_type: str, criteria: Dict[str, Any], 
                      start: int, step: int, limit_step: int = 1) -> Any:
    """
    Fetches data with a backoff strategy to handle HTTP 400/416 errors at end of range.
    Recursively reduces step size to find remaining items.
    Returns:
        - List[Dict]: Items found.
        - int: 0 if End of Range confirmed.
    """
    range_end = start + step - 1
    range_header = f"{start}-{range_end}"
    local_criteria = criteria.copy()
    local_criteria['range'] = range_header
    
    try:
        items = client.make_request(entity_type, local_criteria)
        return items
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [400, 416]:
            # If step is small enough, assume legitimate end of data
            if step <= limit_step:
                logger.info(f"   ℹ️ End of range confirmed (Step {step} failed at {start}).")
                return 0
            
            # Backoff: Try a smaller step (10% of current)
            new_step = max(limit_step, step // 10)
            logger.warning(f"   ⚠️ Range {range_header} rejected (HTTP {e.response.status_code}). Backing off to step {new_step}...")
            
            # Recursive call
            return fetch_with_backoff(client, entity_type, criteria, start, new_step, limit_step)
        raise e
