"""
Validação SQL Direta - Schema SIS
Executa queries SQL diretas no PostgreSQL para validar dados
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433'),
    'database': os.getenv('POSTGRES_DB', 'glpi_data'),
    'user': os.getenv('POSTGRES_USER', 'glpi_user'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def execute_query(cursor, query, description):
    """Execute query and print results."""
    print(f"\n{description}")
    print("-" * 60)
    cursor.execute(query)
    
    # Get column names
    if cursor.description:
        columns = [desc[0] for desc in cursor.description]
        print("  " + " | ".join(columns))
        print("  " + "-" * 50)
        
        # Fetch and print rows
        rows = cursor.fetchall()
        if rows:
            for row in rows[:10]:  # Show first 10 rows
                print("  " + " | ".join(str(v) for v in row))
            if len(rows) > 10:
                print(f"  ... e mais {len(rows) - 10} registros")
        else:
            print("  (sem registros)")
        
        return rows
    return []

def main():
    print("=" * 80)
    print("VALIDAÇÃO SQL DIRETA - SCHEMA SIS")
    print("=" * 80)
    
    try:
        # Connect
        print(f"\n[CONEXÃO] Conectando ao PostgreSQL...")
        print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"  Database: {DB_CONFIG['database']}")
        print(f"  User: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"  ✓ Conectado com sucesso!")
        
        # 1. List all schemas
        execute_query(cursor, """
            SELECT schema_name 
            FROM information_schema.schemata 
            ORDER BY schema_name;
        """, "[1/8] SCHEMAS DISPONÍVEIS")
        
        # 2. List tables in SIS schema
        execute_query(cursor, """
            SELECT table_name, 
                   pg_size_pretty(pg_total_relation_size('sis.' || table_name)) as size
            FROM information_schema.tables 
            WHERE table_schema = 'sis'
            ORDER BY table_name;
        """, "[2/8] TABELAS NO SCHEMA SIS")
        
        # 3. Count records in each SIS table
        print("\n[3/8] CONTAGEM DE REGISTROS EM CADA TABELA SIS")
        print("-" * 60)
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'sis' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        for (table,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM sis.{table};")
            count = cursor.fetchone()[0]
            print(f"  sis.{table}: {count:,} registros")
        
        # 4. Sample data from glpi_entities
        execute_query(cursor, """
            SELECT id, name, completename 
            FROM sis.glpi_entities 
            LIMIT 5;
        """, "[4/8] SAMPLE: sis.glpi_entities (primeiras 5)")
        
        # 5. Sample data from glpi_groups
        execute_query(cursor, """
            SELECT id, name 
            FROM sis.glpi_groups 
            LIMIT 5;
        """, "[5/8] SAMPLE: sis.glpi_groups (primeiras 5)")
        
        # 6. Sample data from tickets
        execute_query(cursor, """
            SELECT id, glpi_id, titulo, status_id, prioridade_id, 
                   entidade_id, categoria_id, criado_em
            FROM sis.tickets 
            LIMIT 5;
        """, "[6/8] SAMPLE: sis.tickets (primeiras 5)")
        
        # 7. Validate foreign keys
        execute_query(cursor, """
            SELECT 
                COUNT(*) as total_tickets,
                COUNT(entidade_id) as tickets_com_entidade,
                COUNT(categoria_id) as tickets_com_categoria,
                COUNT(CASE WHEN entidade_id IS NULL THEN 1 END) as tickets_sem_entidade
            FROM sis.tickets;
        """, "[7/8] VALIDAÇÃO: Foreign Keys nos Tickets")
        
        # 8. Check if any data in other schemas
        print("\n[8/8] VERIFICANDO SE DADOS FORAM PARA OUTRO SCHEMA")
        print("-" * 60)
        
        # Check public schema
        try:
            cursor.execute("SELECT COUNT(*) FROM public.tickets;")
            count = cursor.fetchone()[0]
            print(f"  public.tickets: {count} registros")
        except:
            print("  public.tickets: não existe")
        
        # Check dtic schema
        try:
            cursor.execute("SELECT COUNT(*) FROM dtic.tickets;")
            count = cursor.fetchone()[0]
            print(f"  dtic.tickets: {count} registros")
        except:
            print("  dtic.tickets: erro ao consultar")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("VALIDAÇÃO CONCLUÍDA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
