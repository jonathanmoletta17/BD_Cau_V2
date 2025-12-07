import os
from sqlalchemy import create_engine, text, inspect

# Database connection parameters
user = "glpi_user"
password = "glpi_secure_2024"
host = "127.0.0.1"
port = "5433"
db = "glpi_data"

db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

print("=" * 60)
print("VALIDAÇÃO DO BANCO DE DADOS V3")
print("=" * 60)
print(f"\nConectando em: postgresql://{user}:****@{host}:{port}/{db}")

try:
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("✅ Conexão estabelecida com sucesso!\n")
        
        # Test basic query
        result = conn.execute(text("SELECT version()"))
        pg_version = result.scalar()
        print(f"PostgreSQL Version: {pg_version}\n")
        
        # Check schemas
        print("=" * 60)
        print("SCHEMAS DISPONÍVEIS:")
        print("=" * 60)
        result = conn.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """))
        schemas = [row[0] for row in result]
        for schema in schemas:
            print(f"  • {schema}")
        
        # Check DTIC tables
        print("\n" + "=" * 60)
        print("TABELAS NO SCHEMA 'dtic':")
        print("=" * 60)
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'dtic'
            ORDER BY table_name
        """))
        dtic_tables = [row[0] for row in result]
        
        if not dtic_tables:
            print("❌ Nenhuma tabela encontrada no schema 'dtic'!")
        else:
            for table in dtic_tables:
                # Count rows
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM dtic.{table}"))
                count = count_result.scalar()
                status = "✅" if count > 0 else "⚠️"
                print(f"  {status} {table:30s} - {count:>6} registros")
        
        # Summary
        print("\n" + "=" * 60)
        print("RESUMO:")
        print("=" * 60)
        total_tables = len(dtic_tables)
        populated_tables = sum(1 for table in dtic_tables if conn.execute(text(f"SELECT COUNT(*) FROM dtic.{table}")).scalar() > 0)
        print(f"Total de tabelas: {total_tables}")
        print(f"Tabelas populadas: {populated_tables}")
        print(f"Tabelas vazias: {total_tables - populated_tables}")
        
        if populated_tables == total_tables and total_tables > 0:
            print("\n✅ TODAS AS TABELAS ESTÃO POPULADAS!")
        elif populated_tables > 0:
            print(f"\n⚠️  {total_tables - populated_tables} tabela(s) sem dados.")
        else:
            print("\n❌ BANCO VAZIO - É necessário popular os dados!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    exit(1)
