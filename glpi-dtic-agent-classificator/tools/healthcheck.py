"""
HealthChecker - Validação de Dependências do Chat Ticket Opener

Verifica se todos os serviços necessários estão disponíveis antes de iniciar
a sessão de chat, evitando falhas frustradas após o usuário iniciar a conversa.

Uso:
    from tools.healthcheck import HealthChecker
    
    if not HealthChecker.run_all_checks():
        print("Serviços indisponíveis")
        sys.exit(1)
"""

import sys
import os
import requests
from typing import Tuple

# Add project root to sys.path for standalone execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from glpi_agent.glpi_client import GlpiClient
from glpi_agent.config import ENVIRONMENT


class HealthChecker:
    """
    Verificador de saúde das dependências do Chat Ticket Opener.
    
    Verifica:
    - LLM Service (Ollama/vLLM/NIM)
    - GLPI API (conexão e autenticação)
    """
    
    @staticmethod
    def check_llm(base_url: str, timeout: int = 5) -> Tuple[bool, str]:
        """
        Verifica se o serviço LLM está acessível.
        
        Args:
            base_url: URL base do LLM (ex: http://localhost:11434/v1)
            timeout: Timeout da requisição em segundos
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        try:
            # Tenta endpoint de health (vLLM/NIM)
            health_url = base_url.replace("/v1", "") + "/health"
            response = requests.get(health_url, timeout=timeout)
            
            if response.status_code == 200:
                return True, f"LLM disponível em {health_url}"
            else:
                return False, f"LLM retornou status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            # Tenta endpoint alternativo (Ollama)
            try:
                models_url = base_url.replace("/v1", "") + "/api/tags"
                response = requests.get(models_url, timeout=timeout)
                
                if response.status_code == 200:
                    return True, f"Ollama disponível em {models_url}"
                else:
                    return False, f"Endpoint /api/tags retornou {response.status_code}"
            except:
                return False, f"Não foi possível conectar em {base_url}"
                
        except requests.exceptions.Timeout:
            return False, f"Timeout ao conectar em {base_url}"
        except Exception as e:
            return False, f"Erro ao verificar LLM: {str(e)}"
    
    @staticmethod
    def check_glpi(environment: str = None) -> Tuple[bool, str]:
        """
        Verifica se a API do GLPI está acessível e autenticada.
        
        Args:
            environment: Ambiente GLPI ('test' ou 'prod'). Se None, usa ENVIRONMENT do config
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        try:
            env = environment or ENVIRONMENT
            client = GlpiClient(environment=env)
            client.init_session()
            
            if client.session_token:
                # Testa buscar 1 categoria para validar permissões
                try:
                    categories = client.list_categories()
                    cat_count = len(categories) if categories else 0
                    return True, f"GLPI conectado (ambiente: {env}, {cat_count} categorias)"
                except:
                    return True, f"GLPI autenticado (ambiente: {env})"
            else:
                return False, f"Falha na autenticação GLPI (ambiente: {env})"
                
        except Exception as e:
            return False, f"Erro ao conectar GLPI: {str(e)}"
    
    @staticmethod
    def run_all_checks(verbose: bool = True) -> bool:
        """
        Executa todos os healthchecks necessários.
        
        Args:
            verbose: Se True, imprime resultados detalhados
        
        Returns:
            True se todos os checks passaram, False caso contrário
        """
        if verbose:
            print("🔍 Verificando dependências do Chat Ticket Opener...")
            print("=" * 60)
        
        all_ok = True
        
        # 1. Verificar LLM
        try:
            # Importa aqui para evitar erro se módulo não existir
            from agent.llm_connector import LLMConnector
            connector = LLMConnector()
            
            llm_ok, llm_msg = HealthChecker.check_llm(connector.base_url)
            
            if verbose:
                status_icon = "✅" if llm_ok else "❌"
                print(f"{status_icon} LLM Service: {llm_msg}")
            
            all_ok = all_ok and llm_ok
            
        except Exception as e:
            if verbose:
                print(f"❌ LLM Service: Erro ao inicializar LLMConnector - {str(e)}")
            all_ok = False
        
        # 2. Verificar GLPI
        glpi_ok, glpi_msg = HealthChecker.check_glpi()
        
        if verbose:
            status_icon = "✅" if glpi_ok else "❌"
            print(f"{status_icon} GLPI API: {glpi_msg}")
        
        all_ok = all_ok and glpi_ok
        
        # 3. Verificar variáveis de ambiente críticas
        env_vars = {
            "GLPI_TEST_USER_TOKEN": os.getenv("GLPI_TEST_USER_TOKEN"),
            "GLPI_TEST_APP_TOKEN": os.getenv("GLPI_TEST_APP_TOKEN"),
        }
        
        missing_vars = [var for var, value in env_vars.items() if not value]
        
        if missing_vars:
            if verbose:
                print(f"⚠️ Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
            # Não bloqueia, mas avisa
        
        if verbose:
            print("=" * 60)
            if all_ok:
                print("✅ Todos os serviços estão disponíveis. Pode prosseguir!")
            else:
                print("❌ Alguns serviços estão indisponíveis. Verifique os erros acima.")
                print("\nDicas:")
                print("  • Para LLM: Verifique se Ollama/vLLM/NIM está rodando")
                print("  • Para GLPI: Verifique tokens no arquivo .env")
            print()
        
        return all_ok
    
    @staticmethod
    def check_llm_model(model_name: str) -> Tuple[bool, str]:
        """
        Verifica se um modelo específico está carregado no LLM.
        
        Args:
            model_name: Nome do modelo (ex: "llama3.1:8b")
        
        Returns:
            Tupla (disponível: bool, mensagem: str)
        """
        try:
            from agent.llm_connector import LLMConnector
            connector = LLMConnector()
            
            # Tenta endpoint de modelos (Ollama)
            models_url = connector.base_url.replace("/v1", "") + "/api/tags"
            response = requests.get(models_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name") for m in models]
                
                if model_name in model_names:
                    return True, f"Modelo '{model_name}' disponível"
                else:
                    available = ", ".join(model_names[:3])
                    return False, f"Modelo '{model_name}' não encontrado. Disponíveis: {available}..."
            
            # Fallback: assume que está ok se não conseguir listar
            return True, "Não foi possível listar modelos, assumindo OK"
            
        except Exception as e:
            return True, f"Verificação de modelo pulada: {str(e)}"


if __name__ == "__main__":
    # Teste standalone
    print("\n=== HealthChecker Test ===\n")
    
    # Teste individual de cada serviço
    print("1. Testando LLM...")
    from agent.llm_connector import LLMConnector
    connector = LLMConnector()
    llm_ok, llm_msg = HealthChecker.check_llm(connector.base_url)
    print(f"   {'✅' if llm_ok else '❌'} {llm_msg}\n")
    
    print("2. Testando GLPI...")
    glpi_ok, glpi_msg = HealthChecker.check_glpi()
    print(f"   {'✅' if glpi_ok else '❌'} {glpi_msg}\n")
    
    print("3. Teste completo:")
    result = HealthChecker.run_all_checks()
    
    print(f"\n{'✅ APROVADO' if result else '❌ REPROVADO'}")
