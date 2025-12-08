import os
import pandas as pd
from pandasai import SmartDataframe, Agent
from pandasai.llm import OpenAI
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame, context_info: dict):
        self.df = df
        self.context_info = context_info
        self.llm = self._setup_llm()
        self.agent = None
        if self.llm is not None:
            self.agent = Agent(
                [self.df],
                config={
                    "llm": self.llm,
                    "verbose": True,
                    "save_charts": True,
                    "save_charts_path": os.path.join(os.getcwd(), "output"),
                    "open_charts": False,
                },
                memory_size=10
            )
        
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
            # Fallback: perform built-in analysis without LLM
            try:
                df = self.df.copy()
                df['ano'] = df['criado_em'].dt.year
                # Build metric in hours: prefer tempo_para_resolver, else derive from timestamps
                df['metric_hours'] = None
                if 'tempo_para_resolver' in df.columns:
                    df['metric_hours'] = (df['tempo_para_resolver'].fillna(0) / 3600.0)
                # Derive from timestamps when available
                delta = (df['solucionado_em'] - df['criado_em']).dt.total_seconds()
                df.loc[df['metric_hours'] == 0, 'metric_hours'] = (delta / 3600.0)
                # Keep valid positive values
                df_valid = df.dropna(subset=['metric_hours'])
                df_valid = df_valid[df_valid['metric_hours'] > 0]

                # Compute averages for available years
                years = sorted(df_valid['ano'].dropna().unique().tolist())
                averages = {}
                for y in years:
                    h_mean = df_valid.loc[df_valid['ano'] == y, 'metric_hours'].mean()
                    if pd.notna(h_mean):
                        averages[y] = h_mean

                lines = ['Análise (fallback sem LLM): Tempo médio de resolução por ano']
                if not averages:
                    lines.append('- Não há dados válidos de tempo_para_resolver para calcular.')
                    return "\n".join(lines)

                for ano in sorted(averages.keys()):
                    horas = averages[ano]
                    lines.append(f"- {ano}: ~{horas:.2f} horas")

                # Chart only if we have at least one value
                if len(averages) > 0:
                    output_dir = os.path.join(os.getcwd(), 'output')
                    os.makedirs(output_dir, exist_ok=True)
                    plt.figure(figsize=(6, 4))
                    # Build a series from averages in hours
                    ser = pd.Series({k: v for k, v in averages.items()}).sort_index()
                    ser.plot(kind='bar', color='#3b82f6')
                    plt.ylabel('Tempo médio para resolver (horas)')
                    plt.xlabel('Ano')
                    plt.title('Tempo médio de resolução por ano (fallback)')
                    plt.tight_layout()
                    chart_path = os.path.join(output_dir, 'fallback_tempo_medio_resolucao_por_ano.png')
                    plt.savefig(chart_path)
                    plt.close()
                    lines.append(f"Gráfico salvo em: {chart_path}")

                return "\n".join(lines)
            except Exception as e:
                logger.error(f"Fallback analysis failed: {e}")
                return f"Error: LLM não configurado e fallback falhou: {str(e)}"

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
                return "Error: LLM não configurado."
            response = self.agent.chat(enhanced_query)
            return response
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return f"Error during analysis: {str(e)}"
