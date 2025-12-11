import os
import sys
import secrets
from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from glpi_auth import AuthManager

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
load_dotenv(os.path.join(project_root, ".env"))

app = Flask(__name__, template_folder=os.path.join(current_dir, "templates"), static_folder=os.path.join(current_dir, "static"))
app.config["SECRET_KEY"] = secrets.token_urlsafe(32)

GLPI_URL = (
    os.getenv("GLPI_URL")
    or os.getenv("GLPI_PROD_URL")
    or os.getenv("GLPI_DTIC_URL")
    or ""
).rstrip("/")
GLPI_APP_TOKEN = (
    os.getenv("GLPI_APP_TOKEN")
    or os.getenv("GLPI_PROD_APP_TOKEN")
    or os.getenv("GLPI_DTIC_APP_TOKEN")
    or ""
)

auth_manager = AuthManager()

def sanitize(value: str) -> str:
    if value is None:
        return ""
    cleaned = value.strip()
    # basic sanitization: disallow angle brackets and control chars
    cleaned = cleaned.replace("<", "").replace(">", "")
    cleaned = "".join(ch for ch in cleaned if ord(ch) >= 32)
    return cleaned

def validate_fields(login: str, password: str):
    errors = {}
    if not login:
        errors["login"] = "Usuário é obrigatório"
    if not password:
        errors["password"] = "Senha é obrigatória"
    elif len(password) < 8:
        errors["password"] = "Senha deve ter no mínimo 8 caracteres"
    return errors

@app.get("/")
def index():
    return render_template("login.html")

@app.get("/prefill")
def prefill():
    username = auth_manager.detect_windows_username() or ""
    return jsonify({"username": username})

@app.get("/csrf")
def csrf():
    token = secrets.token_urlsafe(24)
    resp = make_response(jsonify({"token": token}))
    resp.set_cookie("csrf_token", token, httponly=True, samesite="Strict")
    return resp

@app.post("/login")
def login():
    # CSRF check (double submit cookie)
    header_token = request.headers.get("X-CSRF-Token")
    cookie_token = request.cookies.get("csrf_token")
    if not header_token or header_token != cookie_token:
        return jsonify({"ok": False, "error": "CSRF inválido"}), 400
    data = request.get_json(force=True) or {}
    login = sanitize(data.get("login") or "")
    password = sanitize(data.get("password") or "")
    errors = validate_fields(login, password)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    # classify helper
    def classify(status: int, text: str) -> str:
        if status is None:
            return "network_error"
        if "ERROR_WRONG_APP_TOKEN_PARAMETER" in (text or ""):
            return "app_token_invalid"
        if "ERROR_LOGIN" in (text or "") or "Bad login" in (text or ""):
            return "login_invalid"
        if status == 401:
            return "unauthorized"
        if status == 403:
            return "forbidden"
        if status == 404:
            return "not_found"
        if 400 <= status < 500:
            return "client_error"
        if 500 <= status < 600:
            return "server_error"
        return "ok"

    # attempt GET Basic header
    token = auth_manager.glpi_init_session_basic_header(login, password, get_full_session=True)
    if not token:
        # fallback POST credentials
        token = auth_manager.glpi_init_session_credentials(login, password)
        if not token:
            # attempt to infer from status texts via a lightweight probe: since we don't have text here, default to unauthorized
            cls = "unauthorized"
            msg = {
                "login_invalid": "Login ou senha incorretos",
                "app_token_invalid": "App-Token inválido ou IP não permitido",
                "unauthorized": "Não autorizado (401)",
                "server_error": "Erro no servidor GLPI",
                "client_error": "Erro de requisição",
                "network_error": "Erro de rede ou endpoint indisponível",
            }.get(cls, "Falha na autenticação")
            return jsonify({"ok": False, "error": msg, "details": {"class": cls}}), 401
    full = auth_manager.get_my_user(token)
    user = (full or {}).get("session", {}).get("glpifriendlyname")
    return jsonify({"ok": True, "session_token_prefix": token[:10], "user": user})

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    try:
        port = int(os.getenv("PORT", "8000"))
    except ValueError:
        port = 8000
    app.run(host=host, port=port, debug=True)
