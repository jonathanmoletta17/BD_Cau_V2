"""
GLPI API Client - Simplified for V3
Handles authentication, session management, and API requests to GLPI
"""
import requests
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GLPIClient:
    """Simplified GLPI API client with session management and retry logic."""
    
    def __init__(self, base_url: str, app_token: str, user_token: str):
        self.base_url = base_url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        
        if not all([self.base_url, self.app_token, self.user_token]):
            raise ValueError("base_url, app_token, and user_token are required")
        
        self.session_token = None
        self.session = requests.Session()
        self.max_retries = 3
        self.retry_delay = 5
    
    def __enter__(self):
        """Context manager entry - start session."""
        self.init_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.close_session()
    
    def init_session(self):
        """Initialize GLPI session."""
        url = f"{self.base_url}/initSession"
        headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}',
            'Content-Type': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                self.session_token = data.get('session_token')
                
                if not self.session_token:
                    raise Exception("Session token not received")
                
                logger.info(f"✓ GLPI session started")
                return
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to start GLPI session after {self.max_retries} attempts")
    
    def close_session(self):
        """Close GLPI session."""
        if not self.session_token:
            return
        
        url = f"{self.base_url}/killSession"
        headers = {
            'App-Token': self.app_token,
            'Session-Token': self.session_token
        }
        
        try:
            self.session.get(url, headers=headers, timeout=10)
            logger.info("✓ GLPI session closed")
        except Exception as e:
            logger.warning(f"Error closing session: {e}")
        finally:
            self.session_token = None
    
    def make_request(self, endpoint: str, params: Dict = None, method: str = 'GET') -> Dict:
        """Make authenticated request to GLPI API."""
        if not self.session_token:
            raise Exception("Session not initialized")
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'App-Token': self.app_token,
            'Session-Token': self.session_token,
            'Content-Type': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, headers=headers, params=params, timeout=60)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:  # Session expired
                    logger.warning("Session expired, renewing...")
                    self.init_session()
                    headers['Session-Token'] = self.session_token
                    continue
                else:
                    logger.error(f"HTTP Error {response.status_code}: {e}")
                    raise
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
    
    def get_all_pages(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Fetch all pages from an endpoint with automatic pagination."""
        if params is None:
            params = {}
        
        all_items = []
        start = 0
        limit = 1000  # GLPI max range
        
        while True:
            params['range'] = f"{start}-{start + limit - 1}"
            
            try:
                items = self.make_request(endpoint, params)
                
                if not items:
                    break
                
                all_items.extend(items)
                
                # If we got fewer items than requested, we're done
                if len(items) < limit:
                    break
                
                start += limit
                
            except Exception as e:
                # Check if it's a "range exceed" error (end of data)
                if "RANGE_EXCEED" in str(e):
                    break
                logger.error(f"Error fetching pages for {endpoint}: {e}")
                break
        
        return all_items
    
    # Metadata retrieval methods
    def get_entities(self) -> List[Dict]:
        """Get all entities."""
        return self.get_all_pages('Entity')
    
    def get_locations(self) -> List[Dict]:
        """Get all locations."""
        return self.get_all_pages('Location')
    
    def get_groups(self) -> List[Dict]:
        """Get all groups."""
        return self.get_all_pages('Group')
    
    def get_users(self) -> List[Dict]:
        """Get all users."""
        return self.get_all_pages('User')
    
    def get_itil_categories(self) -> List[Dict]:
        """Get all ITIL categories."""
        return self.get_all_pages('ITILCategory')
    
    def get_profiles(self) -> List[Dict]:
        """Get all profiles."""
        return self.get_all_pages('Profile')
    
    def get_groups_users(self) -> List[Dict]:
        """Get all group-user relationships."""
        return self.get_all_pages('Group_User')
    
    def get_profiles_users(self) -> List[Dict]:
        """Get all profile-user relationships."""
        return self.get_all_pages('Profile_User')
    
    # Ticket retrieval methods
    def get_tickets(self, params: Dict = None) -> List[Dict]:
        """Get tickets with optional filters."""
        return self.get_all_pages('Ticket', params)
    
    def get_ticket_users(self, ticket_id: int) -> List[Dict]:
        """Get users associated with a ticket."""
        try:
            return self.make_request(f'Ticket/{ticket_id}/Ticket_User')
        except:
            return []
    
    def get_ticket_groups(self, ticket_id: int) -> List[Dict]:
        """Get groups associated with a ticket."""
        try:
            return self.make_request(f'Ticket/{ticket_id}/Group_Ticket')
        except:
            return []
    
    def get_ticket_changes(self) -> List[Dict]:
        """Get all ticket changes (history)."""
        return self.get_all_pages('TicketTask')
