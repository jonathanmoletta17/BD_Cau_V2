"""
Debug SIS Schema - Investigate Empty Tables
"""
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import Database

def debug_sis_schema():
    print("=" * 80)
    print("DEBUG: INVESTIGATING SIS SCHEMA")
    print("=" * 80)
    
    # Test 1: Check if schema exists
    print("\n[1/5] Verificando se schema 'sis' existe...")
    session = Database.get_session(context="dtic")  # Use dtic to query pg_catalog
    
    result = session.execute(text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name IN ('dtic', 'sis', 'public')
        ORDER BY schema_name;
    """))
    schemas = [row[0] for row in result]
    print(f"  Schemas encontrados: {schemas}")
    
    if 'sis' not in schemas:
        print("  ✗ PROBLEMA: Schema 'sis' NÃO EXISTE!")
        session.close()
        return
    
    print("  ✓ Schema 'sis' existe")
    
    # Test 2: Check tables in SIS schema
    print("\n[2/5] Verificando tabelas no schema 'sis'...")
    result = session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'sis'
        ORDER BY table_name;
    """))
    sis_tables = [row[0] for row in result]
    print(f"  Tabelas no schema sis: {len(sis_tables)}")
    for t in sis_tables[:5]:
        print(f"    - {t}")
    if len(sis_tables) > 5:
        print(f"    ... e mais {len(sis_tables) - 5} tabelas")
    
    # Test 3: Count records in each schema
    print("\n[3/5] Contando registros em cada schema...")
    
    for schema in ['dtic', 'sis', 'public']:
        if schema in schemas:
            print(f"\n  Schema: {schema}")
            
            # Entities
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {schema}.glpi_entities;"))
                count = result.scalar()
                print(f"    glpi_entities: {count}")
            except:
                print(f"    glpi_entities: N/A")
            
            # Tickets
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {schema}.tickets;"))
                count = result.scalar()
                print(f"    tickets: {count}")
            except:
                print(f"    tickets: N/A")
    
    # Test 4: Check schema translation
    print("\n[4/5] Testando schema translation...")
    session.close()
    
    # Try with SIS context
    session_sis = Database.get_session(context="sis")
    
    # Check what schema is being used
    result = session_sis.execute(text("SELECT current_schema();"))
    current = result.scalar()
    print(f"  Current schema (context='sis'): {current}")
    
    # Try to query without schema prefix
    try:
        result = session_sis.execute(text("SELECT COUNT(*) FROM tickets;"))
        count = result.scalar()
        print(f"  COUNT(tickets) sem prefixo: {count}")
    except Exception as e:
        print(f"  Erro ao query sem prefixo: {e}")
    
    session_sis.close()
    
    # Test 5: Check if data went to wrong schema
    print("\n[5/5] Verificando se dados foram para schema errado...")
    session = Database.get_session(context="dtic")
    
    # Check public schema
    try:
        result = session.execute(text("SELECT COUNT(*) FROM public.tickets;"))
        count = result.scalar()
        if count > 0:
            print(f"  ⚠️  AVISO: public.tickets tem {count} registros!")
    except:
        print("  public.tickets: não existe ou vazio")
    
    # Check dtic schema
    try:
        result = session.execute(text("SELECT COUNT(*) FROM dtic.tickets;"))
        count = result.scalar()
        print(f"  dtic.tickets: {count} registros")
    except:
        print("  dtic.tickets: erro ao consultar")
    
    session.close()
    
    print("\n" + "=" * 80)
    print("FIM DO DEBUG")
    print("=" * 80)

if __name__ == "__main__":
    debug_sis_schema()
