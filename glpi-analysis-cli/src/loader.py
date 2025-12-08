import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.years = [2023, 2024, 2025]
        
    def load_data(self) -> pd.DataFrame:
        """
        Loads and merges CSV files for 2023, 2024, 2025.
        Optimizes types for memory usage.
        """
        dfs = []
        
        for year in self.years:
            filename = f"dados_{year}.csv"
            filepath = os.path.join(self.base_path, filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"File {filename} not found. Skipping.")
                continue
                
            logger.info(f"Loading {filename}...")
            
            try:
                # Specify dtypes for efficiency
                df = pd.read_csv(
                    filepath,
                    parse_dates=['criado_em', 'solucionado_em'],
                    dtype={
                        'status_id': 'Int16',
                        'prioridade_id': 'Int8',
                        'tipo_id': 'Int8',
                        'tempo_para_resolver': 'Int32',
                        'categoria': 'category',
                        'entidade': 'category',
                        'localizacao': 'category'
                    }
                )
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                
        if not dfs:
            raise FileNotFoundError("No data files loaded.")
            
        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Combined data: {len(combined_df)} records.")
        
        return combined_df

    def get_context_info(self):
        """Returns metadata about the dataset for the AI."""
        return {
            "columns": [
                {"name": "id", "description": "Ticket ID"},
                {"name": "titulo", "description": "Ticket Title/Subject"},
                {"name": "status_id", "description": "Status Code (1=New, 2=Processing, 3=Planned, 4=Pending, 5=Solved, 6=Closed)"},
                {"name": "prioridade_id", "description": "Priority (1=Very Low to 5=Very High)"},
                {"name": "criado_em", "description": "Creation Date"},
                {"name": "solucionado_em", "description": "Solution Date"},
                {"name": "tempo_para_resolver", "description": "Time to resolve in seconds"},
                {"name": "tecnicos", "description": "Names of technicians assigned (comma separated)"},
                {"name": "categoria", "description": "ITIL Category of the ticket"},
                {"name": "entidade", "description": "Entity/Department"},
            ]
        }
