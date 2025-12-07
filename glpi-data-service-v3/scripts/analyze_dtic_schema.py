"""
Analyze DTIC Database Structure
Purpose: Map complete database schema, tables, and relationships
"""
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433'),
    'database': os.getenv('POSTGRES_DB', 'glpi_data'),
    'user': os.getenv('POSTGRES_USER', 'glpi_user'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def analyze_dtic_schema():
    """Analyze complete DTIC schema structure."""
    
    print("=" * 80)
    print("ANÁLISE COMPLETA DO SCHEMA DTIC")
    print("=" * 80)
    print(f"\n[INFO] Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. List all tables in DTIC schema
        print("[1/6] Listando tabelas no schema DTIC...")
        cursor.execute("""
            SELECT 
                table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname = 'dtic'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"  ✓ Total de tabelas: {len(tables)}\n")
        
        for table_name, size in tables:
            print(f"  - {table_name} ({size})")
        
        # 2. Get row counts for each table
        print("\n[2/6] Contando registros por tabela...")
        table_counts = {}
        for table_name, _ in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM dtic.{table_name};")
                count = cursor.fetchone()[0]
                table_counts[table_name] = count
                print(f"  - {table_name}: {count:,} registros")
            except Exception as e:
                print(f"  ! Erro ao contar {table_name}: {str(e)}")
        
        # 3. Analyze table columns
        print("\n[3/6] Analisando colunas das tabelas principais...")
        main_tables = ['tickets', 'glpi_users', 'glpi_entities', 'glpi_itilcategories']
        
        table_structures = {}
        for table_name in main_tables:
            if table_name in [t[0] for t in tables]:
                cursor.execute(f"""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'dtic' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                
                columns = cursor.fetchall()
                table_structures[table_name] = columns
                print(f"\n  {table_name} ({len(columns)} colunas):")
                for col_name, col_type, nullable, default in columns[:5]:  # Show first 5
                    null_str = "NULL" if nullable == "YES" else "NOT NULL"
                    print(f"    - {col_name}: {col_type} {null_str}")
                if len(columns) > 5:
                    print(f"    ... e mais {len(columns) - 5} colunas")
        
        # 4. Analyze relationships (foreign keys)
        print("\n[4/6] Analisando relacionamentos (foreign keys)...")
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'dtic'
            ORDER BY tc.table_name, kcu.column_name;
        """)
        
        foreign_keys = cursor.fetchall()
        print(f"  ✓ Total de foreign keys: {len(foreign_keys)}\n")
        
        # Group by table
        fk_by_table = {}
        for table, col, fk_table, fk_col in foreign_keys:
            if table not in fk_by_table:
                fk_by_table[table] = []
            fk_by_table[table].append((col, fk_table, fk_col))
        
        for table, fks in fk_by_table.items():
            print(f"  {table}:")
            for col, fk_table, fk_col in fks:
                print(f"    - {col} → {fk_table}.{fk_col}")
        
        # 5. Analyze indexes
        print("\n[5/6] Analisando índices...")
        cursor.execute("""
            SELECT
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'dtic'
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        print(f"  ✓ Total de índices: {len(indexes)}\n")
        
        # Group by table
        idx_by_table = {}
        for table, idx_name, idx_def in indexes:
            if table not in idx_by_table:
                idx_by_table[table] = []
            idx_by_table[table].append(idx_name)
        
        for table, idxs in sorted(idx_by_table.items()):
            print(f"  {table}: {len(idxs)} índices")
        
        # 6. Summary Statistics
        print("\n[6/6] Estatísticas Resumidas...")
        print(f"  ✓ Total de Tabelas: {len(tables)}")
        print(f"  ✓ Total de Registros: {sum(table_counts.values()):,}")
        print(f"  ✓ Tamanho Total Estimado: {sum([int(size.split()[0]) if size.split()[1] == 'kB' else int(size.split()[0]) * 1024 for _, size in tables if 'bytes' not in size and 'MB' not in size])}")
        print(f"  ✓ Tabela com mais registros: {max(table_counts, key=table_counts.get)} ({table_counts[max(table_counts, key=table_counts.get)]:,})")
        
        # Generate summary report
        print("\n" + "=" * 80)
        print("RESUMO DA ESTRUTURA DTIC")
        print("=" * 80)
        
        print("\n### Tabelas Principais:")
        main_tables_list = ['tickets', 'glpi_users', 'glpi_entities', 'glpi_groups', 
                           'glpi_itilcategories', 'glpi_locations', 'ticket_changes']
        for table in main_tables_list:
            if table in table_counts:
                print(f"  - {table}: {table_counts[table]:,} registros")
        
        print("\n### Tabelas de Relacionamento N:N:")
        nn_tables = ['tickets_users', 'tickets_groups', 'glpi_groups_users', 'glpi_profiles_users']
        for table in nn_tables:
            if table in table_counts:
                print(f"  - {table}: {table_counts[table]:,} registros")
        
        print("\n" + "=" * 80)
        
        cursor.close()
        conn.close()
        
        return {
            'tables': tables,
            'counts': table_counts,
            'structures': table_structures,
            'foreign_keys': fk_by_table,
            'indexes': idx_by_table
        }
        
    except Exception as e:
        print(f"\n✗ ERRO: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_dtic_schema()
