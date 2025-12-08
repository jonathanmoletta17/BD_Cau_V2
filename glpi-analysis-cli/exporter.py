import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Config (Default to docker-compose values if not set)
DB_USER = os.getenv("POSTGRES_USER", "glpi_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "glpi_dev_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "glpi_data")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_db_connection():
    engine = create_engine(DATABASE_URL)
    return engine.connect()

def fetch_data():
    print("Connecting to database...")
    conn = get_db_connection()
    
    query = """
    SELECT 
        t.id,
        t.glpi_id,
        t.titulo,
        t.status_id,
        t.prioridade_id,
        t.tipo_id,
        t.criado_em,
        t.solucionado_em,
        t.tempo_para_resolver,
        t.tempo_para_atribuir,
        c.completename as categoria,
        e.completename as entidade,
        l.name as localizacao,
        
        -- Aggregate technicians (type=2)
        (
            SELECT string_agg(u.name, ', ')
            FROM dtic.tickets_users tu
            JOIN dtic.glpi_users u ON u.id = tu.user_id
            WHERE tu.ticket_id = t.id AND tu.type = 2
        ) as tecnicos,
        
        -- Aggregate requesters (type=1)
        (
            SELECT string_agg(u.name, ', ')
            FROM dtic.tickets_users tu
            JOIN dtic.glpi_users u ON u.id = tu.user_id
            WHERE tu.ticket_id = t.id AND tu.type = 1
        ) as requerentes

    FROM dtic.tickets t
    LEFT JOIN dtic.glpi_itilcategories c ON t.categoria_id = c.id
    LEFT JOIN dtic.glpi_entities e ON t.entidade_id = e.id
    LEFT JOIN dtic.glpi_locations l ON t.localizacao_id = l.id
    WHERE t.is_deleted = false
    """
    
    print("Executing query...")
    df = pd.read_sql(text(query), conn)
    conn.close()
    
    # Process dates
    df['criado_em'] = pd.to_datetime(df['criado_em'])
    
    return df

def save_by_year(df):
    years = [2023, 2024, 2025]
    
    for year in years:
        # Filter data for the specific year
        year_df = df[df['criado_em'].dt.year == year]
        
        filename = f"dados_{year}.csv"
        filepath = os.path.join(".", filename)
        
        print(f"Saving {len(year_df)} records to {filename}...")
        year_df.to_csv(filepath, index=False)

if __name__ == "__main__":
    try:
        df = fetch_data()
        print(f"Total records fetched: {len(df)}")
        save_by_year(df)
        print("Export completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
