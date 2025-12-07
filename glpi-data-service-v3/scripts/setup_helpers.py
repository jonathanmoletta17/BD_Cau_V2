"""
Script to create API Helper Views in the database
"""
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Database

def create_helpers():
    print("=" * 60)
    print("CRIANDO VIEWS E FUNÇÕES HELPER")
    print("=" * 60)
    
    session = Database.get_session(context="dtic")
    
    # Ler SQL file
    sql_file = Path(__file__).parent / "create_api_helpers.sql"
    sql_content = sql_file.read_text(encoding='utf-8')
    
    # Executar cada statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    for i, stmt in enumerate(statements, 1):
        try:
            session.execute(text(stmt))
            print(f"[{i}/{len(statements)}] ✓ Executado")
        except Exception as e:
            print(f"[{i}/{len(statements)}] ✗ Erro: {e}")
            raise
    
    session.commit()
    session.close()
    
    print("\n" + "=" * 60)
    print("✓ VIEWS E FUNÇÕES CRIADAS COM SUCESSO!")
    print("=" * 60)
    print("\nViews disponíveis:")
    print("  - v_tickets_api")
    print("  - v_tickets_users_api")
    print("  - v_tickets_groups_api")
    print("  - v_tickets_full_api")
    print("\nFunção disponível:")
    print("  - get_ticket_by_glpi_id(glpi_id)")
    print("=" * 60)

if __name__ == "__main__":
    create_helpers()
