"""
Create SIS Schema - Clone from DTIC Structure
Purpose: Create a parallel schema 'sis' with the same structure as 'dtic'
"""
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433'),
    'database': os.getenv('POSTGRES_DB', 'glpi_data'),
    'user': os.getenv('POSTGRES_USER', 'glpi_user'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def create_sis_schema():
    """Create SIS schema by cloning DTIC structure."""
    
    print("=" * 80)
    print("CRIAÇÃO DO SCHEMA SIS - CLONAGEM DA ESTRUTURA DTIC")
    print("=" * 80)
    print(f"\n[INFO] Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Step 1: Create SIS schema
        print("[1/4] Criando schema 'sis'...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS sis;")
        print("  ✓ Schema 'sis' criado/verificado")
        
        # Step 2: Get all tables from DTIC
        print("\n[2/4] Listando tabelas do schema DTIC...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'dtic'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  ✓ Encontradas {len(tables)} tabelas para clonar")
        
        # Step 3: Clone each table structure
        print("\n[3/4] Clonando estrutura das tabelas...")
        for table_name in tables:
            try:
                # Create table with same structure
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS sis.{table_name} 
                    (LIKE dtic.{table_name} INCLUDING ALL);
                """)
                print(f"  ✓ {table_name}")
            except Exception as e:
                print(f"  ✗ Erro ao clonar {table_name}: {str(e)}")
                raise
        
        # Step 4: Verify creation
        print("\n[4/4] Verificando tabelas criadas no schema SIS...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'sis'
            ORDER BY table_name;
        """)
        
        sis_tables = [row[0] for row in cursor.fetchall()]
        print(f"  ✓ Total de tabelas no schema SIS: {len(sis_tables)}")
        
        # Verify all tables were created
        missing_tables = set(tables) - set(sis_tables)
        if missing_tables:
            print(f"\n  ⚠ ATENÇÃO: Tabelas não criadas: {missing_tables}")
        else:
            print("\n  ✓ Todas as tabelas foram clonadas com sucesso!")
        
        # Commit changes
        conn.commit()
        
        # Summary
        print("\n" + "=" * 80)
        print("RESUMO DA CRIAÇÃO")
        print("=" * 80)
        print(f"\n  ✓ Schema: sis")
        print(f"  ✓ Tabelas criadas: {len(sis_tables)}")
        print(f"  ✓ Status: {'SUCESSO TOTAL' if not missing_tables else 'PARCIAL - Verificar avisos'}")
        
        # List main tables
        print("\n  Principais tabelas criadas:")
        main_tables = ['tickets', 'glpi_users', 'glpi_entities', 'glpi_groups', 
                      'glpi_itilcategories', 'tickets_users', 'tickets_groups']
        for table in main_tables:
            if table in sis_tables:
                print(f"    - sis.{table}")
        
        print("\n" + "=" * 80)
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERRO CRÍTICO: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = create_sis_schema()
    exit(0 if success else 1)
