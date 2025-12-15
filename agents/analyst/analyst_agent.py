import pandas as pd
import requests
import json
import re
import os
from typing import Optional, Any
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Configuration
OLLAMA_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:9000/v1")
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "Qwen/Qwen2.5-Coder-7B-Instruct-AWQ")

# DB Config
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "glpi_data")
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class GLPIAnalystAgent:
    def __init__(self):
        try:
            print(f"🔌 Init DB Engine: {DB_HOST}:{DB_PORT} ({DB_USER})")
            self.engine = create_engine(DATABASE_URL)
            self.df = self._load_real_data()
        except Exception as e:
            print(f"❌ Init Error: {e}")
            self.df = self._load_mock_data()
    
    def _load_real_data(self) -> pd.DataFrame:
        """Loads real GLPI data from PostgreSQL (Tickets + Locations)."""
        # Optimized query using LEFT JOIN directly in SQL to avoid Pandas Merge Type Errors
        sql = """
        SELECT 
            t.id, 
            t.titulo, 
            t.status_id, 
            t.prioridade_id, 
            t.impact, 
            t.urgency, 
            t.criado_em,
            l.name as local_nome
        FROM dtic.tickets t
        LEFT JOIN dtic.glpi_locations l ON t.localizacao_id = l.id
        WHERE t.is_deleted = false
        LIMIT 2000
        """
        
        try:
            print(f"🔌 Connecting to DB...")
            df = pd.read_sql(sql, self.engine)
            print(f"✅ Loaded {len(df)} tickets with locations.")
            
            # Mappings for LLM Friendliness
            status_map = {1: "New", 2: "Processing", 3: "Plan", 4: "Waiting", 5: "Solved", 6: "Closed"}
            urgency_map = {1: "Muito Baixa", 2: "Baixa", 3: "Media", 4: "Alta", 5: "Muito Alta"}
            prioridade_map = {1: "Muito Baixa", 2: "Baixa", 3: "Media", 4: "Alta", 5: "Muito Alta"}
            
            df['status_name'] = df['status_id'].map(status_map).fillna("Unknown")
            df['urgency_name'] = df['urgency'].map(urgency_map).fillna("Unknown")
            df['priority_name'] = df['prioridade_id'].map(prioridade_map).fillna("Unknown")
            
            # Clean up ID columns to reduce noise
            df = df.drop(columns=['status_id', 'urgency', 'prioridade_id', 'impact'])
            
            return df
        except Exception as e:
            print(f"❌ DB Error Detail: {e}")
            import traceback
            traceback.print_exc()
            raise e

    # --- NEW ANALYTICAL TOOLS (Direct SQL) ---
    
    def get_ticket_timeline(self, ticket_id: int) -> list:
        """Returns the full timeline of a ticket (human readable)."""
        sql = """
        SELECT 
            tc.data_mudanca,
            tc.usuario_nome,
            tc.campo,
            tc.valor_antigo,
            tc.valor_novo,
            t.titulo
        FROM dtic.ticket_changes tc
        JOIN dtic.tickets t ON tc.ticket_id = t.id
        WHERE t.glpi_id = %s
        ORDER BY tc.data_mudanca ASC
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), (ticket_id,)).fetchall()
                
            timeline = []
            for row in result:
                # Basic formatting logic
                desc = f"Mudou {row.campo} de '{row.valor_antigo}' para '{row.valor_novo}'"
                if row.campo == 'content': desc = "Adicionou comentário"
                
                timeline.append({
                    "time": row.data_mudanca.strftime("%Y-%m-%d %H:%M") if row.data_mudanca else "",
                    "actor": row.usuario_nome,
                    "action": desc
                })
            return timeline
        except Exception as e:
            return [f"Error fetching timeline: {e}"]

    def get_ticket_health(self, ticket_id: int) -> dict:
        """Returns health metrics for a ticket."""
        sql = """
        SELECT tc.campo, tc.valor_antigo, tc.valor_novo, tc.data_mudanca
        FROM dtic.ticket_changes tc
        JOIN dtic.tickets t ON tc.ticket_id = t.id
        WHERE t.glpi_id = %s
        """
        try:
            with self.engine.connect() as conn:
                changes = conn.execute(text(sql), (ticket_id,)).fetchall()
            
            ping_pong = sum(1 for c in changes if c.campo in ['technician', 'group'])
            reopens = 0
            for c in changes:
                if c.campo == 'status':
                    old_v = str(c.valor_antigo).lower()
                    new_v = str(c.valor_novo).lower()
                    if ('solucionado' in old_v or 'fechado' in old_v) and \
                       ('processando' in new_v or 'novo' in new_v):
                        reopens += 1
            
            return {
                "ticket_id": ticket_id,
                "reatribuicoes": ping_pong,
                "reaberturas": reopens,
                "saude": "Ruim" if ping_pong > 3 or reopens > 0 else "Boa"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_process_bottlenecks(self, days: int = 30) -> list:
        """Returns process bottlenecks (avg time in status) for last X days."""
        sql = """
            WITH StatusChanges AS (
                SELECT 
                    ticket_id,
                    valor_novo as status_nome,
                    data_mudanca as start_time,
                    LEAD(data_mudanca) OVER (PARTITION BY ticket_id ORDER BY data_mudanca) as end_time
                FROM dtic.ticket_changes
                WHERE campo = 'status'
                  AND data_mudanca >= NOW() - INTERVAL '%s days'
            )
            SELECT 
                status_nome,
                COUNT(*) as ocorrencias,
                AVG(EXTRACT(EPOCH FROM (COALESCE(end_time, NOW()) - start_time))/3600)::NUMERIC(10,2) as media_horas
            FROM StatusChanges
            WHERE end_time IS NOT NULL
            GROUP BY status_nome
            ORDER BY media_horas DESC
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql % days)).fetchall() # Simple param sub for interval
            
            return [{"status": r.status_nome, "avg_hours": float(r.media_horas)} for r in result]
        except Exception as e:
            return [f"Error: {e}"]

    def _load_mock_data(self) -> pd.DataFrame:
        """Loads sample GLPI data for analysis (Fallback)."""
        data = {
            "id": [1, 2, 3, 4, 5],
            "title": ["PC não liga", "Impressora sem papel", "Erro 404 no SIS", "Solicitação de Acesso", "Wifi Lento"],
            "status_name": ["New", "Processing", "Closed", "New", "Pending"], # Updated to match real schema key
            "urgency": [5, 3, 5, 1, 3], # Numeric to match DB
            "criado_em": ["2023-10-01", "2023-10-02", "2023-10-03", "2023-10-04", "2023-10-05"]
        }
        return pd.DataFrame(data)

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Calls local LLM via Ollama."""
        api_url = f"{OLLAMA_BASE_URL}/chat/completions"
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "stream": False
        }
        try:
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling LLM: {e}"

    def _generate_code(self, query: str) -> str:
        """Generates Pandas code to analyze the data."""
        # Create a summary of the dataframe to help the LLM
        data_summary = []
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                unique_vals = self.df[col].unique().tolist()
                if len(unique_vals) > 10:
                    unique_vals = unique_vals[:10] + ["..."]
                data_summary.append(f"- {col}: {unique_vals}")
            else:
                data_summary.append(f"- {col}: {self.df[col].dtype}")
        
        summary_str = "\n".join(data_summary)
        
        prompt = f"""
        You are a Senior Python Data Analyst.
        Given a Pandas DataFrame `df` with the following structure:
        {summary_str}
        
        AND the following Special Tools available via `self`:
        - `self.get_ticket_timeline(ticket_id: int) -> list`: Get full history/timeline of a ticket.
        - `self.get_ticket_health(ticket_id: int) -> dict`: Get health metrics (reopens, ping-pong).
        - `self.get_process_bottlenecks(days: int) -> list`: Get global process bottlenecks (avg time in status).
        
        Write Python code to answer: "{query}"
        
        Rules:
        1. Use `df` variable directly for general stats.
        2. Use `self.get_...` for specific ticket deep-dives or global history analysis.
        3. Assign the result to a variable named `result`.
        4. Do NOT plot. Return text/number results only.
        5. Return ONLY the code inside ```python``` blocks.
        6. Match string values EXACTLY as shown in the structure above.
        
        Example 1 (General):
        ```python
        result = df[df['status_name'] == 'New'].count()['id']
        ```
        
        Example 2 (Specific Ticket):
        ```python
        result = self.get_ticket_timeline(11909)
        ```
        """
        
        llm_response = self._call_llm("You are a Python Data Analyst. Output ONLY valid Python code.", prompt)
        print(f"🐛 DEBUG LLM Response:\n{llm_response}\n---")
        return self._extract_code(llm_response)

    def _extract_code(self, text: str) -> str:
        """Extracts code buffer from markdown."""
        match = re.search(r"```python(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _execute_code(self, code: str) -> Any:
        """Executes the generated code."""
        local_env = {"df": self.df, "pd": pd, "self": self}
        try:
            exec(code, {}, local_env)
            return local_env.get("result", "No result variable found.")
        except Exception as e:
            return f"Execution Error: {e}"

    def _explain_result(self, query: str, result: Any) -> str:
        """Explains the result in natural language."""
        prompt = f"""
        User Question: "{query}"
        Analysis Result: "{result}"
        
        Explain this result to the user in Portuguese (PT-BR) clearly and concisely.
        """
        return self._call_llm("You are a helpful assistant.", prompt)

    def run(self, query: str) -> str:
        """Main pipeline: Query -> Code -> Result -> Explanation."""
        print(f"🔎 Analyzing: {query}")
        
        # 1. Generate Code
        code = self._generate_code(query)
        print(f"💻 Generated Code:\n{code}")
        
        # 2. Execute Code
        result = self._execute_code(code)
        print(f"📊 Result: {result}")
        
        # 3. Explain
        explanation = self._explain_result(query, result)
        return explanation

if __name__ == "__main__":
    agent = GLPIAnalystAgent()
    
    # Test queries
    queries = [
        "Quantos chamados estão com urgência Alta?",
        "Qual a sala com mais problemas?",
        "Liste os chamados de Hardware."
    ]
    
    for q in queries:
        print("\n" + "="*50)
        answer = agent.run(q)
        print(f"🤖 Agent: {answer}")
