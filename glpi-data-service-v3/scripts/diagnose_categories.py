"""
Diagnóstico de Categorias - GLPI vs Banco Local
Verifica duplicações e inconsistências no banco de dados.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
from dotenv import load_dotenv

load_dotenv(project_root / '.env')

def get_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5433'),
        database=os.getenv('POSTGRES_DB', 'glpi_data'),
        user=os.getenv('POSTGRES_USER', 'glpi_user'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def diagnose_categories():
    """Diagnóstico completo de categorias."""
    print("=" * 60)
    print("DIAGNÓSTICO DE CATEGORIAS - GLPI vs BANCO LOCAL")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Verificar schemas existentes
    print("\n[1] SCHEMAS EXISTENTES")
    print("-" * 40)
    cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name;
    """)
    schemas = [row[0] for row in cursor.fetchall()]
    print(f"Schemas encontrados: {schemas}")
    
    # 2. Verificar tabelas de categorias em cada schema
    print("\n[2] TABELAS DE CATEGORIAS POR SCHEMA")
    print("-" * 40)
    
    for schema in schemas:
        cursor.execute(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = '{schema}' 
            AND table_name LIKE '%categor%'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  {schema}: {tables if tables else 'Nenhuma tabela de categorias'}")
    
    # 3. Contar categorias em cada schema
    print("\n[3] CONTAGEM DE CATEGORIAS POR SCHEMA")
    print("-" * 40)
    
    total_categorias = 0
    for schema in schemas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {schema}.glpi_itilcategories;")
            count = cursor.fetchone()[0]
            print(f"  {schema}.glpi_itilcategories: {count} registros")
            total_categorias += count
        except Exception as e:
            print(f"  {schema}.glpi_itilcategories: Tabela não existe ou erro: {e}")
            conn.rollback()
    
    print(f"\n  TOTAL GERAL: {total_categorias} categorias no banco")
    
    # 4. Verificar duplicações por ID
    print("\n[4] VERIFICAÇÃO DE DUPLICAÇÕES")
    print("-" * 40)
    
    for schema in schemas:
        try:
            cursor.execute(f"""
                SELECT id, COUNT(*) as cnt 
                FROM {schema}.glpi_itilcategories 
                GROUP BY id 
                HAVING COUNT(*) > 1
                ORDER BY cnt DESC
                LIMIT 10;
            """)
            duplicates = cursor.fetchall()
            if duplicates:
                print(f"  {schema}: {len(duplicates)} IDs duplicados!")
                for dup in duplicates[:5]:
                    print(f"    ID {dup[0]}: {dup[1]} ocorrências")
            else:
                print(f"  {schema}: Nenhum ID duplicado ✓")
        except Exception as e:
            print(f"  {schema}: Erro ao verificar: {e}")
            conn.rollback()
    
    # 5. Listar categorias únicas por nome
    print("\n[5] TOP 20 CATEGORIAS (por nome)")
    print("-" * 40)
    
    for schema in schemas:
        try:
            cursor.execute(f"""
                SELECT id, name, completename 
                FROM {schema}.glpi_itilcategories 
                ORDER BY id
                LIMIT 20;
            """)
            categories = cursor.fetchall()
            if categories:
                print(f"\n  Schema: {schema}")
                for cat in categories:
                    name = cat[1] or '(sem nome)'
                    completename = cat[2] or ''
                    print(f"    [{cat[0]:4}] {name[:50]}")
        except Exception as e:
            print(f"  {schema}: Erro: {e}")
            conn.rollback()
    
    # 6. Verificar categorias com level (hierarquia)
    print("\n[6] DISTRIBUIÇÃO POR NÍVEL HIERÁRQUICO")
    print("-" * 40)
    
    for schema in schemas:
        try:
            cursor.execute(f"""
                SELECT level, COUNT(*) as cnt 
                FROM {schema}.glpi_itilcategories 
                GROUP BY level 
                ORDER BY level;
            """)
            levels = cursor.fetchall()
            if levels:
                print(f"\n  Schema: {schema}")
                for level in levels:
                    lvl = level[0] if level[0] is not None else 'NULL'
                    print(f"    Nível {lvl}: {level[1]} categorias")
        except Exception as e:
            print(f"  {schema}: Erro: {e}")
            conn.rollback()
    
    # 7. Categorias raiz (level 1 ou parent_id NULL)
    print("\n[7] CATEGORIAS RAIZ (nível 1)")
    print("-" * 40)
    
    for schema in schemas:
        try:
            cursor.execute(f"""
                SELECT id, name 
                FROM {schema}.glpi_itilcategories 
                WHERE level = 1 OR parent_id IS NULL OR parent_id = 0
                ORDER BY name;
            """)
            roots = cursor.fetchall()
            if roots:
                print(f"\n  Schema: {schema} - {len(roots)} categorias raiz:")
                for root in roots:
                    print(f"    [{root[0]:4}] {root[1]}")
        except Exception as e:
            print(f"  {schema}: Erro: {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO COMPLETO")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_categories()
