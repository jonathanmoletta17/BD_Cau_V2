"""
GLPI Integrations Common - GLPI API Client
Handles authentication and session management.
"""
import requests
import time
import logging
from typing import List, Dict, Optional

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
        self.init_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()
    
    def init_session(self):
        url = f"{self.base_url}/initSession"
        headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}'
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
        if not self.session_token:
            return
        url = f"{self.base_url}/killSession"
        headers = {'App-Token': self.app_token, 'Session-Token': self.session_token}
        try:
            self.session.get(url, headers=headers, timeout=10)
        except Exception:
            pass
        finally:
            self.session_token = None
            
    def make_request(self, endpoint: str, params: Dict = None, method: str = 'GET', json_data: Dict = None) -> Dict:
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
                elif method.upper() == 'POST':
                    response = self.session.post(url, headers=headers, json=json_data, timeout=60)
                
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    logger.warning("Session expired, renewing...")
                    self.init_session()
                    headers['Session-Token'] = self.session_token
                    continue
                logger.error(f"HTTP Error {response.status_code}: {e}")
                raise
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def get_all_pages(self, endpoint: str, params: Dict = None) -> List[Dict]:
        if params is None: params = {}
        all_items = []
        start = 0
        limit = 1000
        while True:
            params['range'] = f"{start}-{start + limit - 1}"
            try:
                items = self.make_request(endpoint, params)
                if not items: break
                all_items.extend(items)
                if len(items) < limit: break
                start += limit
            except Exception as e:
                if "RANGE_EXCEED" in str(e): break
                logger.error(f"Error fetching pages for {endpoint}: {e}")
                break
        return all_items

    # Metadata Getters
    def get_users(self) -> List[Dict]:
        return self.get_all_pages('User')

    def get_groups(self) -> List[Dict]:
        return self.get_all_pages('Group')

    def get_entities(self) -> List[Dict]:
        return self.get_all_pages('Entity')

    def get_locations(self) -> List[Dict]:
        return self.get_all_pages('Location')

    def get_itil_categories(self) -> List[Dict]:
        return self.get_all_pages('ITILCategory')
        
    def get_profiles(self) -> List[Dict]:
        return self.get_all_pages('Profile')

    def get_groups_users(self) -> List[Dict]:
        return self.get_all_pages('Group_User')

    def get_profiles_users(self) -> List[Dict]:
        return self.get_all_pages('Profile_User')
