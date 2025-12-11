import requests
import os
from dotenv import load_dotenv
import base64
import getpass

# Carregar variáveis de ambiente do projeto raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
load_dotenv(os.path.join(project_root, ".env"))

GLPI_URL = (
    os.getenv("GLPI_URL")
    or os.getenv("GLPI_PROD_URL")
    or os.getenv("GLPI_DTIC_URL")
    or "http://glpi.example.com/apirest.php"
).rstrip("/")
GLPI_APP_TOKEN = (
    os.getenv("GLPI_APP_TOKEN")
    or os.getenv("GLPI_PROD_APP_TOKEN")
    or os.getenv("GLPI_DTIC_APP_TOKEN")
    or "CHANGE_ME"
)

class AuthManager:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "App-Token": GLPI_APP_TOKEN,
            "Content-Type": "application/json"
        }
    def glpi_init_session_credentials(self, login, password):
        """
        Autentica no GLPI usando Login e Senha (recomendado para usuários finais).
        """
        url = f"{GLPI_URL}/initSession"
        payload = {"login": login, "password": password}

        try:
            response = self.session.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            session_token = data.get("session_token")
            return session_token
        except Exception as e:
            return None

    def glpi_init_session_basic_header(self, login, password, get_full_session=False):
        url = f"{GLPI_URL}/initSession"
        headers = self.headers.copy()
        token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {token}"
        try:
            r = self.session.get(
                f"{url}{'?get_full_session=true' if get_full_session else ''}",
                headers=headers
            )
            r.raise_for_status()
            data = r.json()
            return data.get("session_token")
        except Exception as e:
            return None

    def detect_windows_username(self):
        try:
            return os.getlogin()
        except Exception:
            pass
        try:
            return getpass.getuser()
        except Exception:
            pass
        return os.environ.get("USERNAME") or os.environ.get("USER") or ""

    def get_my_user(self, session_token):
        """
        Obtém dados do usuário logado.
        """
        url = f"{GLPI_URL}/getFullSession"
        headers = self.headers.copy()
        headers["Session-Token"] = session_token
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
