import os
import pandas as pd
from pandasai import SmartDataframe, Agent
from pandasai.llm import OpenAI
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame, context_info: dict):
        self.df = self._clean_raw_data(df)
        self.context_info = context_info
        self.llm = self._setup_llm()
        self.agent = None
        if self.llm is not None:
            self.agent = Agent(
                [self.df],
                config={
                    "llm": self.llm,
                    "verbose": True,
                    "custom_whitelisted_dependencies": ["seaborn", "matplotlib"],
                    "save_charts": True,
                    "save_charts_path": os.path.join(os.getcwd(), "output"),
                    "open_charts": False,
                },
                memory_size=10
            )

    def _clean_raw_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the dataframe to ensure compatibility with Matplotlib and PandasAI.
        Handles 'NAType' and prevents 'mixed datetimes and integers' errors by being selective.
        """
        clean_df = df.copy()

        # 1. Clean Numeric Columns (Fill NaN with 0 for plotting safety)
        numeric_cols = ['tempo_para_resolver', 'tempo_para_solucao', 'impacto', 'urgencia', 'prioridade']
        for col in numeric_cols:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce').fillna(0)

        # 2. Clean Datetime Columns (Convert to datetime, keep NaT for invalid)
        # CRITICAL: Do NOT fill dates with 0, or pandas.to_datetime will crash on mixed types.
        date_cols = ['criado_em', 'solucionado_em']
        for col in date_cols:
            if col in clean_df.columns:
                clean_df[col] = pd.to_datetime(clean_df[col], errors='coerce')

        # 3. Clean String Columns (Fill NaN with empty string to avoid object-check failures)
        # Identify object columns that are NOT date cols
        for col in clean_df.columns:
            if clean_df[col].dtype == 'object' and col not in date_cols:
                 clean_df[col] = clean_df[col].fillna("")
        
        return clean_df
        
    def _setup_llm(self):
        api_key = os.getenv("OPENAI_API_KEY", "dummy")
        api_base = os.getenv("OPENAI_API_BASE")
        model_name = os.getenv("LLM_MODEL_NAME")
        
        if not api_base and not os.getenv("OPENAI_API_KEY"):
             logger.warning("No LLM configuration found (OPENAI_API_KEY or OPENAI_API_BASE). Using fallback mode.")
             return None

        # PandasAI valida o nome do modelo contra uma lista hardcoded de modelos OpenAI conhecidos.
        # Para usar um modelo customizado (NIM, Ollama, etc), precisamos 'enganar' a validação ou não passar o nome,
        # dependendo da versão. Na versão 2.2.0, é mais seguro instanciar sem validar ou usar um nome genérico se o base_url for custom.
        # Mas o OpenAI wrapper do PandasAI tenta validar.
        
        # Workaround: Se estamos usando um endpoint customizado (NIM), passamos o nome mas o PandasAI pode reclamar.
        # Uma alternativa é usar a classe LangChain ou Generic se disponível, mas vamos tentar configurar o OpenAI client para ignorar.
        
        llm = OpenAI(
            api_token=api_key,
            api_base=api_base
        )
        
        # Forçamos o nome do modelo manualmente após a inicialização para evitar a validação do construtor
        if model_name:
            llm.model = model_name
            
        return llm

    def analyze(self, query: str):
        """
        Process a natural language query using PandasAI.
        """
        if not self.llm:
            return self._fallback(query)

        logger.info(f"Analyzing query: {query}")
        
        # Add context to the query to improve results
        enhanced_query = f"""
        Act as a senior Data Scientist for DTIC.
        Context: {self.context_info}
        
        Question: {query}
        
        Please provide a detailed analysis. If plotting, use matplotlib/seaborn.
        """
        
        try:
            if self.agent is None:
                return self._fallback(query)
            response = self.agent.chat(enhanced_query)
            return response
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._fallback(query)

    def _fallback(self, query: str):
        q = (query or "").lower()
        try:
            if "tempo médio" in q or "tempo medio" in q:
                return self._fallback_time_per_year()
            if "categoria" in q and ("maior" in q or "mais" in q) and any(y in q for y in ["2023","2024","2025"]):
                target_year = 2025
                for y in [2023, 2024, 2025]:
                    if str(y) in q:
                        target_year = y
                        break
                return self._fallback_top_category(target_year)
            if "técnic" in q or "tecnic" in q:
                if "30" in q and "dias" in q:
                    return self._fallback_top_technicians_last_days(30)
                return self._fallback_top_technicians_last_days(90)
            return self._fallback_time_per_year()
        except Exception as e:
            logger.error(f"Fallback failed: {e}")
            return f"Erro no fallback: {str(e)}"

    def _fallback_time_per_year(self):
        df = self.df.copy()
        df['ano'] = df['criado_em'].dt.year
        df['metric_hours'] = None
        if 'tempo_para_resolver' in df.columns:
            df['metric_hours'] = (df['tempo_para_resolver'].fillna(0) / 3600.0)
        delta = (df['solucionado_em'] - df['criado_em']).dt.total_seconds()
        df.loc[df['metric_hours'] == 0, 'metric_hours'] = (delta / 3600.0)
        df_valid = df.dropna(subset=['metric_hours'])
        df_valid = df_valid[df_valid['metric_hours'] > 0]
        years = sorted(df_valid['ano'].dropna().unique().tolist())
        averages = {}
        for y in years:
            h_mean = df_valid.loc[df_valid['ano'] == y, 'metric_hours'].mean()
            if pd.notna(h_mean):
                averages[y] = h_mean
        lines = ['Tempo médio de resolução por ano']
        if not averages:
            lines.append('Sem dados válidos para calcular.')
            return "\n".join(lines)
        for ano in sorted(averages.keys()):
            horas = averages[ano]
            lines.append(f"- {ano}: ~{horas:.2f} horas")
        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(6, 4))
        ser = pd.Series({k: v for k, v in averages.items()}).sort_index()
        ser.plot(kind='bar', color='#3b82f6')
        plt.ylabel('Horas')
        plt.xlabel('Ano')
        plt.title('Tempo médio de resolução por ano')
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'tempo_medio_resolucao_por_ano.png')
        plt.savefig(chart_path)
        plt.close()
        lines.append(f"Gráfico: {chart_path}")
        return "\n".join(lines)

    def _fallback_top_category(self, year: int):
        df = self.df.copy()
        df_year = df[df['criado_em'].dt.year == year]
        counts = df_year['categoria'].dropna().value_counts()
        top = counts.head(10)
        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(8, 5))
        top[::-1].plot(kind='barh', color='#10b981')
        plt.xlabel('Tickets')
        plt.ylabel('Categoria')
        plt.title(f'Top categorias por número de tickets em {year}')
        plt.tight_layout()
        chart_path = os.path.join(output_dir, f'top_categorias_{year}.png')
        plt.savefig(chart_path)
        plt.close()
        lines = [f"Top categorias em {year}:"]
        for cat, cnt in top.items():
            lines.append(f"- {cat}: {cnt}")
        lines.append(f"Gráfico: {chart_path}")
        return "\n".join(lines)

    def _fallback_top_technicians_last_days(self, days: int):
        df = self.df.copy()
        now = pd.Timestamp.utcnow()
        window_start = now - pd.Timedelta(days=days)
        df = df.dropna(subset=['solucionado_em'])
        df = df[df['solucionado_em'] >= window_start]
        tech_series = df['tecnicos'].dropna().astype(str)
        techs = tech_series.str.split(',').explode().str.strip()
        counts = techs.value_counts().head(10)
        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(8, 5))
        counts[::-1].plot(kind='barh', color='#f59e0b')
        plt.xlabel('Tickets resolvidos')
        plt.ylabel('Técnico')
        plt.title(f'Top técnicos nos últimos {days} dias')
        plt.tight_layout()
        chart_path = os.path.join(output_dir, f'top_tecnicos_{days}d.png')
        plt.savefig(chart_path)
        plt.close()
        lines = [f"Top técnicos nos últimos {days} dias:"]
        for name, cnt in counts.items():
            lines.append(f"- {name}: {cnt}")
        lines.append(f"Gráfico: {chart_path}")
        return "\n".join(lines)
