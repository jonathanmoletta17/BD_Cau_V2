import json
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error
import urllib.parse
import ssl
import time

from glpi_agent.config import (
    ENVIRONMENT,
    GLPI_TEST_URL,
    GLPI_TEST_USER_TOKEN,
    GLPI_TEST_APP_TOKEN,
    GLPI_PROD_URL,
    GLPI_PROD_USER_TOKEN,
    GLPI_PROD_APP_TOKEN,
    HTTPS_ONLY,
    CA_BUNDLE_PATH,
    CACHE_TTL_SECONDS,
)
from glpi_agent.cache import Cache


class GlpiClient:
    def __init__(self, environment: Optional[str] = None, url: Optional[str] = None, user: Optional[str] = None, app: Optional[str] = None):
        self.session_token: Optional[str] = None
        self.cache = Cache(CACHE_TTL_SECONDS)
        self.env = environment or ENVIRONMENT
        self.override = {"url": url, "user": user, "app": app}

    def _creds(self) -> Dict[str, str]:
        if all(self.override.values()):
            return {
                "url": self.override["url"],
                "user": self.override["user"],
                "app": self.override["app"],
            }
        if self.env == "prod":
            return {
                "url": GLPI_PROD_URL,
                "user": GLPI_PROD_USER_TOKEN,
                "app": GLPI_PROD_APP_TOKEN,
            }
        return {
            "url": GLPI_TEST_URL,
            "user": GLPI_TEST_USER_TOKEN,
            "app": GLPI_TEST_APP_TOKEN,
        }

    def _ssl_context(self):
        if CA_BUNDLE_PATH:
            return ssl.create_default_context(cafile=CA_BUNDLE_PATH)
        return ssl.create_default_context()

    def init_session(self) -> None:
        cfg = self._creds()
        url = cfg["url"].strip("/") + "/initSession/"
        if HTTPS_ONLY and url.startswith("http://") and self.env == "prod":
            raise RuntimeError("HTTPS obrigatório em produção")
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"user_token {cfg['user']}",
                "App-Token": cfg["app"],
            },
        )
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.session_token = data.get("session_token")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f"   ERROR init_session HTTP {e.code}: {error_body}")
            self.session_token = None
        except Exception as e:
            print(f"   ERROR init_session: {str(e)}")
            self.session_token = None

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.session_token:
            h["Session-Token"] = self.session_token
        cfg = self._creds()
        if cfg["app"]:
            h["App-Token"] = cfg["app"]
        return h

    def _get(self, url: str) -> Optional[Any]:
        key = f"GET:{url}"
        if self.env == "prod":
            cached = self.cache.get(key)
            if cached is not None:
                return cached
        headers = self._headers()
        headers["Range"] = "items=0-499"
        req = urllib.request.Request(url, method="GET", headers=headers)
        ctx = self._ssl_context()
        tries = 3
        backoff = 0.5
        for _ in range(tries):
            try:
                with urllib.request.urlopen(req, context=ctx) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if self.env == "prod":
                        self.cache.set(key, data)
                    return data
            except Exception:
                time.sleep(backoff)
                backoff *= 2
        return None

    def search_items(self, itemtype: str, params: Dict[str, str]) -> List[Dict]:
        cfg = self._creds()
        q = "?" + "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items()]) if params else ""
        url = cfg["url"].strip("/") + f"/{itemtype}/" + q
        if HTTPS_ONLY and url.startswith("http://") and self.env == "prod":
            raise RuntimeError("HTTPS obrigatório em produção")
        data = self._get(url)
        if isinstance(data, list):
            return data
        return []

    def list_uncategorized_tickets(self) -> List[Dict]:
        items = self.search_items("Ticket", {"is_deleted": "0"})
        res: List[Dict] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            cat = it.get("itilcategories_id")
            if cat in (None, 0, "0", ""):
                res.append(it)
        return res

    def list_categorized_tickets(self) -> List[Dict]:
        items = self.search_items("Ticket", {"is_deleted": "0"})
        res: List[Dict] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            cat = it.get("itilcategories_id")
            if cat not in (None, 0, "0", ""):
                res.append(it)
        return res

    def get_user_by_email(self, email: str) -> Optional[int]:
        """
        Searches for a user by email using the explicit GLPI Search API criteria.
        Returns the User ID if found, otherwise None.
        """
        if not email or "@" not in email:
            return None
            
        # Field 5 = Email
        # Field 2 = ID (forcedisplay to ensure it is returned)
        import urllib.parse
        encoded_email = urllib.parse.quote(email)
        
        # Criteria 5 (Email) contains/equals email
        query = f"/search/User?criteria[0][field]=5&criteria[0][searchtype]=contains&criteria[0][value]={encoded_email}&forcedisplay[0]=2"
        
        cfg = self._creds()
        url = cfg["url"].strip("/") + query
        
        try:
            data = self._get(url)
            if isinstance(data, dict):
                # Check 'data' list
                results = data.get("data", [])
                if results and isinstance(results, list):
                    for user in results:
                        # GLPI returns fields keyed by ID. 
                        # ID is key "2" (int) or sometimes just in the object if forced.
                        # Based on debug: "2": 4020
                        uid = user.get("2")
                        if uid:
                            return int(uid)
            return None
        except Exception as e:
            print(f"Error searching user by email: {e}")
            return None

    def get_user_by_phone_or_email(self, identifier: str) -> Optional[int]:
        """
        Attempts to find a User ID by checking:
        1. mobile (Exact match or contains)
        2. phone (Exact match or contains)
        3. email (Exact match)
        """
        # Search by Mobile
        # Note: GLPI Search API is tricky. We'll try exact matches first via criteria if possible,
        # but search_items here just appends params.
        # "mobile": identifier
        
        # 1. Try Mobile
        users = self.search_items("User", {"mobile": identifier, "is_deleted": "0"})
        if users and isinstance(users, list) and len(users) > 0:
            return int(users[0]['id'])
            
        # 2. Try Phone
        users = self.search_items("User", {"phone": identifier, "is_deleted": "0"})
        if users and isinstance(users, list) and len(users) > 0:
            return int(users[0]['id'])
            
        # 3. Try Email (if identifier looks like email)
        if "@" in identifier:
             users = self.search_items("User", {"email": identifier, "is_deleted": "0"})
             if users and isinstance(users, list) and len(users) > 0:
                return int(users[0]['id'])

        return None

    def update_ticket_category(self, ticket_id: int, category_name: str) -> bool:
        if self.env == "prod":
            return False
        cfg = self._creds()
        url = cfg["url"].strip("/") + "/Ticket/" + str(ticket_id)
        body = json.dumps({"input": {"itilcategories_id": category_name}}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="PUT", headers=self._headers())
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                return True
        except Exception:
            return False

    def add_followup(self, ticket_id: int, message: str) -> bool:
        if self.env == "prod":
            return False
        cfg = self._creds()
        url = cfg["url"].strip("/") + "/Ticket/" + str(ticket_id) + "/ITILFollowup/"
        body = json.dumps({"input": {"content": message}}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers=self._headers())
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                return True
        except Exception:
            return False

    def list_ticket_followups(self, ticket_id: int) -> List[Dict]:
        """Fetch all followups for a specific ticket."""
        cfg = self._creds()
        url = cfg["url"].strip("/") + "/Ticket/" + str(ticket_id) + "/ITILFollowup/"
        data = self._get(url)
        if isinstance(data, list):
            return data
        return []

    def list_categories(self) -> List[Dict[str, Any]]:
        # Use robust range fetching to get all categories (up to 1000)
        return self.list_items_range("ITILCategory", 0, 999)

    def categories_map(self) -> Dict[str, int]:
        items = self.list_categories()
        m: Dict[str, int] = {}
        print(f"DEBUG: categories_map fetched {len(items)} items.")
        for it in items:
            try:
                name = str(it.get("completename", "")).strip()
                if not name:
                     name = str(it.get("name", "")).strip()
                
                # Normalize spaces around separator if needed (GLPI uses " > ")
                # Our context uses " > " (space gt space).
                
                cid = int(it.get("id"))
            except Exception:
                continue
            if name:
                m[name] = cid
        return m

    def create_category(self, name: str) -> Optional[int]:
        if self.env == "prod":
            return None
        cfg = self._creds()
        url = cfg["url"].strip("/") + "/ITILCategory/"
        body = json.dumps({"input": {"name": name}}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers=self._headers())
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict):
                    return int(data.get("id")) if data.get("id") else None
                return None
        except Exception:
            return None

    def create_ticket(self, name: str, content: str, category_id: Optional[int], urgency: int = 3, impact: int = 3, requester_id: Optional[int] = None) -> Optional[int]:
        if self.env == "prod":
            return None
        cfg = self._creds()
        url = cfg["url"].strip("/") + "/Ticket/"
        payload = {
            "name": name, 
            "content": content,
            "urgency": urgency,
            "impact": impact
        }
        if category_id is not None:
            payload["itilcategories_id"] = category_id
        
        if requester_id is not None:
            payload["_users_id_requester"] = requester_id

        # Create Ticket first
        body = json.dumps({"input": payload}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers=self._headers())
        
        new_ticket_id = None
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict):
                    new_ticket_id = int(data.get("id")) if data.get("id") else None
        except Exception:
            return None
            
        # Link Requester if Ticket created and ID provided
        # Note: If _users_id_requester worked, this might fail with 400 (Duplicate).
        # We try anyway to be sure.
        if new_ticket_id and requester_id:
            try:
                # Add Requester (type 1 = Requester)
                link_url = cfg["url"].strip("/") + "/Ticket_User/"
                link_payload = {
                    "tickets_id": new_ticket_id,
                    "users_id": requester_id,
                    "type": 1  # 1=Requester, 2=Observer, 3=Assignee
                }
                link_body = json.dumps({"input": link_payload}).encode("utf-8")
                link_req = urllib.request.Request(link_url, data=link_body, method="POST", headers=self._headers())
                with urllib.request.urlopen(link_req, context=self._ssl_context()) as resp:
                    pass # Success
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8')
                # Ignore 400 if it's likely "Already exists"
                if e.code == 400:
                     print(f"DEBUG: Link requester {requester_id} to {new_ticket_id} returned 400 (Likely already added): {err_body}")
                else:
                     print(f"Failed to link requester {requester_id} to ticket {new_ticket_id}: HTTP {e.code}: {err_body}")
            except Exception as e:
                print(f"Failed to link requester {requester_id} to ticket {new_ticket_id}: {e}")
                
        return new_ticket_id

    def get_item(self, itemtype: str, item_id: int) -> Optional[Dict[str, Any]]:
        cfg = self._creds()
        url = cfg["url"].strip("/") + f"/{itemtype}/" + str(item_id)
        data = self._get(url)
        if isinstance(data, dict):
            return data
        return None

    def get_category_name(self, category_id: Optional[int]) -> str:
        if not category_id:
            return ""
        x = self.get_item("ITILCategory", int(category_id))
        if not x:
            return ""
        return str(x.get("name", "")).strip()

    def list_items_range(self, itemtype: str, start: int, end: int) -> List[Dict[str, Any]]:
        cfg = self._creds()
        # Try passing range in Query String as well, as some GLPI setups ignore the Header
        url = cfg["url"].strip("/") + f"/{itemtype}/?range={start}-{end}"
        headers = self._headers()
        headers["Range"] = f"items={start}-{end}"
        req = urllib.request.Request(url, method="GET", headers=headers)
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []

    def delete_item(self, itemtype: str, item_id: int) -> bool:
        """
        Delete an item from GLPI
        
        Args:
            itemtype: Type of item (e.g., 'ITILCategory', 'Ticket')
            item_id: ID of the item to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if self.env == "prod":
            # Safety: never delete in production
            return False
            
        cfg = self._creds()
        url = cfg["url"].strip("/") + f"/{itemtype}/{item_id}"
        req = urllib.request.Request(url, method="DELETE", headers=self._headers())
        
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                # Successful deletion returns status 200 or 204
                return resp.status in [200, 204]
        except urllib.error.HTTPError as e:
            # Some APIs return 404 if already deleted, consider it success
            if e.code == 404:
                return True
            return False
        except Exception:
            return False

    def create_item(self, itemtype: str, data: Dict) -> Optional[int]:
        """
        Create an item in GLPI
        
        Args:
            itemtype: Type of item (e.g., 'ITILCategory', 'Ticket')
            data: Dictionary with item fields
            
        Returns:
            New item ID if successful, None otherwise
        """
        if self.env == "prod":
            # Safety: never create in production via this method
            return None
            
        cfg = self._creds()
        url = cfg["url"].strip("/") + f"/{itemtype}/"
        
        body = json.dumps({"input": data}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers=self._headers())
        
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if isinstance(result, dict) and 'id' in result:
                    return int(result['id'])
                return None
        except urllib.error.HTTPError as e:
            # Log HTTP error for debugging
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f"   DEBUG: HTTP {e.code} creating {itemtype}: {error_body[:200]}")
            return None
        except Exception as e:
            print(f"   DEBUG: Exception creating {itemtype}: {str(e)}")
            return None

    def update_item(self, itemtype: str, item_id: int, data: Dict) -> bool:
        """
        Update an item in GLPI
        
        Args:
            itemtype: Type of item (e.g., 'Ticket', 'ITILCategory')
            item_id: ID of the item to update
            data: Dictionary with fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        if self.env == "prod":
            # Safety: never update in production via this method
            return False
            
        cfg = self._creds()
        url = cfg["url"].strip("/") + f"/{itemtype}/{item_id}"
        
        body = json.dumps({"input": data}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="PUT", headers=self._headers())
        
        try:
            with urllib.request.urlopen(req, context=self._ssl_context()) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                # GLPI returns updated item or success array
                return True
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f"   DEBUG: HTTP {e.code} updating {itemtype}/{item_id}: {error_body[:200]}")
            return False
        except Exception as e:
            print(f"   DEBUG: Exception updating {itemtype}/{item_id}: {str(e)}")
            return False
