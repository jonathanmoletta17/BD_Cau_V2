
import unittest
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

class TestRealDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            cls.engine = create_engine(db_url)
            with cls.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            print(f"Skipping Integration Tests: Could not connect to REAL DB: {e}")
            cls.engine = None

    def test_tickets_table_schema(self):
        if not self.engine:
            self.skipTest("No DB Connection")
            
        with self.engine.connect() as conn:
            # Verifica tipo da coluna localizacao_id
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'dtic' 
                AND table_name = 'tickets' 
                AND column_name = 'localizacao_id'
            """)).fetchone()
            
            self.assertIsNotNone(result, "Coluna localizacao_id não existe!")
            print(f"\n✅ Tipo Real da Coluna localizacao_id: {result[0]}")
            
            # Valida se é compatível com INT (o que causou o erro antes)
            is_int = result[0] in ['integer', 'bigint', 'smallint']
            if not is_int:
                print(f"⚠️ AVISO: Coluna é {result[0]}, não INTEGER. O código Python deve tratar isso.")

    def test_ticket_changes_data(self):
        if not self.engine:
            self.skipTest("No DB Connection")
            
        with self.engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM dtic.ticket_changes")).scalar()
            self.assertTrue(count > 0, "Tabela ticket_changes está vazia! Testes de IA falharão.")
            print(f"\n✅ Dados encontrados: {count} logs de mudança.")

if __name__ == '__main__':
    unittest.main()
