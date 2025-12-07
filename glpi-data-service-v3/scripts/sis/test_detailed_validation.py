"""
SIS Detailed Validation - Execute SQL Criteria from Documentation
"""
import sys
from pathlib import Path
import psycopg2
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config

DB_CONFIG = {
    'host': config.POSTGRES_HOST,
    'port': config.POSTGRES_PORT,
    'database': config.POSTGRES_DB,
    'user': config.POSTGRES_USER,
    'password': config.POSTGRES_PASSWORD
}

def execute_and_display(cursor, title, query):
    """Execute query and display results."""
    print(f"\n{title}")
    print("-" * 70)
    print(f"Query: {query.strip()}\n")
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("  ✓ PASS: No results (as expected)")
    else:
        print(f"  Results ({len(results)} rows):")
        for row in results:
            print(f"    {row}")
    
    return results

def main():
    print("=" * 80)
    print("SIS DETAILED VALIDATION - SQL CRITERIA")
    print("=" * 80)
    print(f"Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # ========================================================================
    # 4.1 INTEGRIDADE DE DADOS
    # ========================================================================
    print("\n" + "=" * 80)
    print("4.1 INTEGRIDADE DE DADOS")
    print("=" * 80)
    
    # Test: Data Population
    execute_and_display(cursor, "[1/7] Data Population - glpi_entities", 
        "SELECT COUNT(*) FROM sis.glpi_entities;")
    
    execute_and_display(cursor, "[2/7] Data Population - glpi_groups", 
        "SELECT COUNT(*) FROM sis.glpi_groups;")
    
    execute_and_display(cursor, "[3/7] Data Population - glpi_itilcategories", 
        "SELECT COUNT(*) FROM sis.glpi_itilcategories;")
    
    execute_and_display(cursor, "[4/7] Data Population - glpi_locations", 
        "SELECT COUNT(*) FROM sis.glpi_locations;")
    
    # Test: Required Fields
    print("\n\n[5/7] Required Fields - Checking NULLs in name columns")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_entities WHERE name IS NULL;")
    null_entities = cursor.fetchone()[0]
    print(f"  glpi_entities with NULL name: {null_entities}")
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_groups WHERE name IS NULL;")
    null_groups = cursor.fetchone()[0]
    print(f"  glpi_groups with NULL name: {null_groups}")
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_itilcategories WHERE name IS NULL;")
    null_categories = cursor.fetchone()[0]
    print(f"  glpi_itilcategories with NULL name: {null_categories}")
    
    total_nulls = null_entities + null_groups + null_categories
    if total_nulls == 0:
        print(f"  ✓ PASS: 0 NULLs in required fields")
    else:
        print(f"  ✗ FAIL: {total_nulls} NULLs found")
    
    # ========================================================================
    # 4.2 QUALIDADE DE DADOS
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("4.2 QUALIDADE DE DADOS")
    print("=" * 80)
    
    # Test: Duplicate IDs
    results = execute_and_display(cursor, "[6/7] Duplicate IDs - glpi_entities", """
        SELECT id, COUNT(*) 
        FROM sis.glpi_entities 
        GROUP BY id 
        HAVING COUNT(*) > 1;
    """)
    
    if not results:
        print("  ✓ PASS: No duplicates in glpi_entities")
    else:
        print(f"  ✗ FAIL: {len(results)} duplicate IDs found")
    
    results = execute_and_display(cursor, "[7/7] Duplicate IDs - glpi_groups", """
        SELECT id, COUNT(*) 
        FROM sis.glpi_groups 
        GROUP BY id 
        HAVING COUNT(*) > 1;
    """)
    
    if not results:
        print("  ✓ PASS: No duplicates in glpi_groups")
    else:
        print(f"  ✗ FAIL: {len(results)} duplicate IDs found")
    
    # Test: Sync Timestamps
    print("\n\n[8/9] Sync Timestamps - Recent sync check")
    print("-" * 70)
    print("Query: SELECT COUNT(*) FROM sis.glpi_entities WHERE sincronizado_em > NOW() - INTERVAL '24 hours';\n")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sis.glpi_entities 
        WHERE sincronizado_em > NOW() - INTERVAL '24 hours';
    """)
    recent = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_entities;")
    total = cursor.fetchone()[0]
    
    percentage = (recent / total * 100) if total > 0 else 0
    print(f"  Recent records (< 24h): {recent}/{total} ({percentage:.1f}%)")
    
    if recent == total:
        print("  ✓ PASS: 100% of records synced recently")
    elif percentage >= 95:
        print(f"  ⚠ WARN: {percentage:.1f}% synced recently")
    else:
        print(f"  ✗ FAIL: Only {percentage:.1f}% synced recently")
    
    # ========================================================================
    # 4.3 CONSISTÊNCIA COM API
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("4.3 CONSISTÊNCIA COM API")
    print("=" * 80)
    print("\n[9/9] API vs DB Count Comparison")
    print("-" * 70)
    
    # Get DB counts
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_entities;")
    db_entities = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_groups;")
    db_groups = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_itilcategories;")
    db_categories = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sis.glpi_locations;")
    db_locations = cursor.fetchone()[0]
    
    print(f"  Database counts:")
    print(f"    - Entities: {db_entities}")
    print(f"    - Groups: {db_groups}")
    print(f"    - Categories: {db_categories}")
    print(f"    - Locations: {db_locations}")
    print(f"    - Total: {db_entities + db_groups + db_categories + db_locations}")
    
    # Try to get API counts
    try:
        from src.core.glpi_client import GLPIClient
        
        with GLPIClient(
            config.GLPI_SIS_URL,
            config.GLPI_SIS_APP_TOKEN,
            config.GLPI_SIS_USER_TOKEN
        ) as client:
            api_entities = len(client.get_entities())
            api_groups = len(client.get_groups())
            api_categories = len(client.get_itil_categories())
            api_locations = len(client.get_locations())
            
            print(f"\n  API counts:")
            print(f"    - Entities: {api_entities}")
            print(f"    - Groups: {api_groups}")
            print(f"    - Categories: {api_categories}")
            print(f"    - Locations: {api_locations}")
            
            print(f"\n  Comparison:")
            match = True
            
            if api_entities == db_entities:
                print(f"    ✓ Entities: MATCH ({db_entities})")
            else:
                diff = abs(api_entities - db_entities)
                pct = (diff / api_entities * 100) if api_entities > 0 else 0
                print(f"    ✗ Entities: MISMATCH (API:{api_entities}, DB:{db_entities}, diff:{diff}, {pct:.1f}%)")
                match = False
            
            if api_groups == db_groups:
                print(f"    ✓ Groups: MATCH ({db_groups})")
            else:
                diff = abs(api_groups - db_groups)
                pct = (diff / api_groups * 100) if api_groups > 0 else 0
                print(f"    ✗ Groups: MISMATCH (API:{api_groups}, DB:{db_groups}, diff:{diff}, {pct:.1f}%)")
                match = False
            
            if api_categories == db_categories:
                print(f"    ✓ Categories: MATCH ({db_categories})")
            else:
                diff = abs(api_categories - db_categories)
                pct = (diff / api_categories * 100) if api_categories > 0 else 0
                print(f"    ✗ Categories: MISMATCH (API:{api_categories}, DB:{db_categories}, diff:{diff}, {pct:.1f}%)")
                match = False
            
            if api_locations == db_locations:
                print(f"    ✓ Locations: MATCH ({db_locations})")
            else:
                diff = abs(api_locations - db_locations)
                pct = (diff / api_locations * 100) if api_locations > 0 else 0
                print(f"    ✗ Locations: MISMATCH (API:{api_locations}, DB:{db_locations}, diff:{diff}, {pct:.1f}%)")
                match = False
            
            if match:
                print(f"\n  ✓ PASS: All counts match between API and DB")
            else:
                print(f"\n  ✗ FAIL: Mismatches detected")
    
    except Exception as e:
        print(f"\n  ⚠ WARN: Could not fetch API counts: {str(e)[:50]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("DETAILED VALIDATION COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
