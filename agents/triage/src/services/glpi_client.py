import httpx
import base64
import os
from typing import Optional, Dict, Any, List
from src.config import settings
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class GLPIClient:
    def __init__(self):
        # 1. Configure READ Source (Always PROD) - For Authentication
        self.read_url = settings.GLPI_PROD_URL or settings.GLPI_API_URL
        self.read_app_token = settings.GLPI_PROD_APP_TOKEN or settings.GLPI_APP_TOKEN
        
        # 2. Configure WRITE Target (Test or Prod) - For Actions (Tickets, Categories)
        target = settings.OPENER_TARGET_ENV.lower()
        if target == 'prod':
            self.write_url = settings.GLPI_PROD_URL or settings.GLPI_API_URL
            self.write_app_token = settings.GLPI_PROD_APP_TOKEN or settings.GLPI_APP_TOKEN
            self.write_user_token = settings.GLPI_PROD_USER_TOKEN or settings.GLPI_USER_TOKEN
        else:
            # Default to Test
            self.write_url = settings.GLPI_TEST_URL or self.read_url
            self.write_app_token = settings.GLPI_TEST_APP_TOKEN or self.read_app_token
            self.write_user_token = settings.GLPI_TEST_USER_TOKEN or ""
            
        self.session_token = None
        self.client = httpx.AsyncClient(verify=False, timeout=30.0)
        
        logger.info(f"GLPIClient Initialized. Auth Source: {self.read_url} | Action Target: {self.write_url} ({target.upper()})")

    async def login_on_prod(self, login: str, password: str) -> Dict[str, Any]:
        """
        Authenticates against PROD environment to verify user identity.
        Does not maintain a persistent session.
        """
        # --- MOCK AUTH BYPASS (Dev/Instability Fix) ---
        if settings.MOCK_AUTH_ENABLED:
            logger.warning(f"MOCK AUTH ENABLED: Bypassing Prod Login for {login}")
            # Simple check against env vars (or allow 'glpi'/'glpi' as fallback)
            mock_user = os.getenv("MOCK_AUTH_USER", "glpi")
            mock_pass = os.getenv("MOCK_AUTH_PASS", "glpi")
            
            if login == mock_user and password == mock_pass:
                # Mock a successful Session Response
                return {
                    "ok": True, 
                    "class": "ok", 
                    "user_data": {
                        "session_token": "mock_session_token_xyz",
                        "session": {
                            "glpifriendlyname": f"{login} (Mock)",
                            "glpiactive_entity": 0,
                            "glpidefault_entity": 0,
                            "name": login
                        }
                    }
                }
            else:
                return {"ok": False, "class": "login_invalid", "detail": "Mock Auth Failed"}
        # -----------------------------------------------

        if not self.read_url or not self.read_app_token:
             return {"ok": False, "class": "config_error", "detail": "PROD URL not configured"}

        url = f"{self.read_url}/initSession"
        headers = {
            "App-Token": self.read_app_token,
            "Content-Type": "application/json"
        }
        
        # Basic Auth Construction
        token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("utf-8")
        auth_header = headers.copy()
        auth_header["Authorization"] = f"Basic {token}"
        
        try:
            # Try to init session to validate creds
            response = await self.client.get(f"{url}?get_full_session=true", headers=auth_header)
            
            if response.status_code == 200:
                data = response.json()
                # Kill this prod session immediately as we don't need it
                sess = data.get("session_token")
                if sess:
                    await self._kill_session(self.read_url, self.read_app_token, sess)
                
                return {"ok": True, "class": "ok", "user_data": data}
            
            logger.error(f"Login failed [Status {response.status_code}]: {response.text}")
            return {"ok": False, "class": "login_invalid", "detail": f"GLPI Error: {response.text}"}
            
        except Exception as e:
            logger.error(f"Login on Prod failed: {e}")
            return {"ok": False, "class": "network_error", "detail": str(e)}

    async def _kill_session(self, base_url: str, app_token: str, session_token: str):
        try:
            url = f"{base_url}/killSession"
            headers = {"App-Token": app_token, "Session-Token": session_token}
            await self.client.get(url, headers=headers)
        except:
            pass

    async def init_session(self) -> bool:
        """Initializes a session on the TARGET (Write) environment using Service Token."""
        if self.session_token:
            return True
            
        url = f"{self.write_url}/initSession"
        headers = {
            "App-Token": self.write_app_token,
        }
        if self.write_user_token:
            headers["Authorization"] = f"user_token {self.write_user_token}"
            
        try:
            response = await self.client.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Session Init Failed [{response.status_code}]: {response.text}")
            response.raise_for_status()
            data = response.json()
            self.session_token = data.get("session_token")
            logger.info(f"Initialized GLPI Session on Target")
            return True
        except Exception as e:
            logger.error(f"Failed to init session on target: {e}")
            return False

    async def search_user_id(self, username: str) -> Optional[int]:
        """Searches for User ID in the TARGET environment."""
        if not self.session_token:
            await self.init_session()
            
        url = f"{self.write_url}/User"
        # Criteria: Field 1 (Login/Name), Exact Match
        params = {
            "criteria[0][field]": 1, 
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": username
        }
        headers = {
            "App-Token": self.write_app_token,
            "Session-Token": self.session_token
        }
        
        try:
            response = await self.client.get(url, headers=headers, params=params)
            
            if response.status_code in [200, 206]:
                users = response.json()
                if isinstance(users, list):
                    for u in users:
                        if u.get('name') == username:
                            return u.get('id')
            return None
        except Exception as e:
            logger.error(f"Search user failed: {e}")
            return None

    async def create_ticket(self, title: str, description: str, category_id: int, 
                          ticket_type: int = 1, urgency: int = 3, impact: int = 3, 
                          requester_id: int = None, ai_analysis: str = None, entities_id: int = None):
        """Creates a ticket in the Target Environment"""
        if not self.session_token:
            success = await self.init_session()
            if not success:
                raise Exception("Could not initialize GLPI session")

        full_content = description
        if ai_analysis:
            full_content += f"\n\n---\n**🧠 Análise da IA**\n{ai_analysis}"

        payload = {
            "input": {
                "name": title,
                "content": full_content,
                "itilcategories_id": category_id,
                "type": ticket_type,
                "urgency": urgency,
                "impact": impact
            }
        }
        
        # Override requester if provided
        if requester_id:
            payload["input"]["_users_id_requester"] = requester_id
            
        # Override entity if provided
        if entities_id:
            payload["input"]["entities_id"] = entities_id

        url = f"{self.write_url}/Ticket"
        headers = {
            "App-Token": self.write_app_token,
            "Session-Token": self.session_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"Ticket Created: {response.json().get('id')}")
            return response.json()
        except Exception as e:
            logger.error(f"Create Ticket Failed: {e}")
            raise

    async def get_all_categories(self):
        """Fetches all active ITIL Categories from Target GLPI."""
        if not self.session_token:
            await self.init_session()
        
        url = f"{self.write_url}/ITILCategory"
        headers = {
            "App-Token": self.write_app_token,
            "Session-Token": self.session_token
        }
        params = {"range": "0-999", "is_active": 1}
        
        try:
            response = await self.client.get(url, headers=headers, params=params)
             # Handle empty or error gracefully
            if response.status_code == 200:
                 return response.json()
            return []
        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            return []

    async def update_ticket(self, ticket_id: int, category_id: int):
        """Updates the category of an existing ticket."""
        if not self.session_token:
            await self.init_session()

        url = f"{self.write_url}/Ticket/{ticket_id}"
        headers = {
            "App-Token": self.write_app_token,
            "Session-Token": self.session_token
        }
        payload = {
            "input": {
                "itilcategories_id": category_id
            }
        }
        
        try:
            response = await self.client.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update ticket {ticket_id}: {e}")
            raise
