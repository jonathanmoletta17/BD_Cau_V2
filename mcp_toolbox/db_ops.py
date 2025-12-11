import psycopg2
import json
import os

# Configuration (Env vars should be loaded, but defaulting for safety in this script)
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "glpi_data")
DB_USER = os.getenv("POSTGRES_USER", "glpi_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "glpi_secure_2024")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def list_tables(schema="public"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # If schema is 'all', list from all user schemas
        if schema == 'all':
             cur.execute("""
                SELECT table_schema || '.' || table_name 
                FROM information_schema.tables 
                WHERE table_schema IN ('public', 'dtic', 'sis') 
                AND table_type = 'BASE TABLE';
            """)
        else:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_type = 'BASE TABLE';
            """, (schema,))
            
        tables = [row[0] for row in cur.fetchall()]
        return tables
    finally:
        conn.close()

def get_table_schema(table_name, schema="public"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = %s;
        """, (schema, table_name))
        columns = []
        for row in cur.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == "YES"
            })
        return columns
    finally:
        conn.close()

def run_read_only_sql(query):
    # Security check: Basic SQL Injection / Mutation prevention
    normalized = query.strip().upper()
    if not normalized.startswith("SELECT") and not normalized.startswith("EXPLAIN"):
        raise ValueError("Only SELECT or EXPLAIN queries are allowed.")
    
    if any(x in normalized for x in ["; DROP", "; DELETE", "; UPDATE", "; INSERT", "; ALTER", "; TRUNCATE"]):
        raise ValueError("Dangerous keywords detected.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query)
        
        # Fetch columns
        col_names = [desc[0] for desc in cur.description] if cur.description else []
        results = []
        for row in cur.fetchall():
            # Convert row to dict
            results.append(dict(zip(col_names, row)))
            
        return results
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
