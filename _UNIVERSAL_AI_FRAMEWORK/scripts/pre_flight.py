import os
import sys
import socket
import psycopg2
from dotenv import load_dotenv, find_dotenv

def check_env_file():
    """Verifica se o arquivo .env existe."""
    env_path = find_dotenv()
    if not env_path:
        print("[FAIL] .env file not found!")
        return False
    print(f"[OK] .env found at: {env_path}")
    load_dotenv(env_path)
    return True

def check_postgres_connection():
    """Tenta conectar ao banco de dados REAL."""
    # Prioriza localhost se estiver rodando localmente
    host = os.getenv("POSTGRES_HOST_LOCAL", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    dbname = os.getenv("POSTGRES_DB", "postgres")

    print(f"[INFO] Testing DB Connection to {host}:{port} ({user}@{dbname})...")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=5
        )
        conn.close()
        print("[OK] Database Connection: OK")
        return True
    except Exception as e:
        print(f"[FAIL] Database Connection FAILED: {e}")
        print("   -> Tip: Check if Docker container is running.")
        print("   -> Tip: Check if POSTGRES_HOST_LOCAL is set correctly in .env")
        return False

def check_ollama():
    """Verifica se o servidor de IA local está rodando."""
    host = "localhost"
    port = 11434 # Default Ollama
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        print("[OK] Ollama Service: OK (Port 11434 open)")
        return True
    else:
        print("[WARN] Ollama Service: NOT DETECTED on port 11434 (Is it running?)")
        return False # Warning only

def run_checks():
    print("[INFO] AI-Native Development: Pre-Flight Check")
    print("="*50)
    
    checks = [
        check_env_file,
        check_postgres_connection,
        check_ollama
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("[OK] SYSTEM READY FOR AI DEVELOPMENT")
        sys.exit(0)
    else:
        print("[FAIL] SYSTEM NOT READY. Fix issues before asking AI to code.")
        sys.exit(1)

if __name__ == "__main__":
    run_checks()
