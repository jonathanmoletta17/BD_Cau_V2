
import pytest
import os
import sys
from sqlalchemy import text, create_engine
from dotenv import load_dotenv, find_dotenv

# Setup Paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load Real Env
load_dotenv(find_dotenv())

# Force Localhost for Testing
os.environ["POSTGRES_HOST"] = "localhost" 

@pytest.fixture(scope="module")
def db_engine():
    """Fixture que conecta no banco REAL."""
    db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        yield engine
    except Exception as e:
        pytest.fail(f"Could not connect to REAL DB: {e}")

def test_tickets_table_schema(db_engine):
    """Valida se a tabela tickets tem as colunas esperadas (evita erro de merge)."""
    with db_engine.connect() as conn:
        # Verifica tipo da coluna localizacao_id
        result = conn.execute(text("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'dtic' 
            AND table_name = 'tickets' 
            AND column_name = 'localizacao_id'
        """)).fetchone()
        
        assert result is not None, "Coluna localizacao_id não existe!"
        # O erro anterior foi tentar merge de object com int. Vamos ver o que é.
        print(f"\nTipo Real da Coluna localizacao_id: {result[0]}")

def test_ticket_changes_data(db_engine):
    """Verifica se existem dados na tabela ticket_changes para teste."""
    with db_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM dtic.ticket_changes")).scalar()
        assert count > 0, "Tabela ticket_changes está vazia! Testes de IA falharão."
