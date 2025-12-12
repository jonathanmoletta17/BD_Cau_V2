import yaml
import json
import requests
from pathlib import Path
from typing import List, Dict, Any
try:
    from .schemas import TicketContext
except ImportError:
    from schemas import TicketContext
import os


class SurgicalOpenerAgent:
    def __init__(self, model_name: str = None, ollama_url: str = None):
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
        # Tenta resolver a URL pela variável específica ou pela BASE_URL adaptada
        default_url = "http://host.docker.internal:11434/api/generate"
        ollama_env = os.getenv("OLLAMA_GENERATE_URL")
        base_env = os.getenv("LLM_BASE_URL")
        
        if ollama_env:
            self.ollama_url = start_url = ollama_env
        elif base_env:
            # Tenta adaptar a base url (ex: http://host:9000/v1 -> http://host:11434/api/generate)
            # Mas se for OpenAI API, o payload muda. 
            # Por segurança, vamos assumir que se o usuário definiu BASE_URL, ele quer usar aquilo,
            # mas este agente espera OLLAMA NATIVO.
            # Vamos manter o default do docker internal se não tiver a var especifica OLLAMA_GENERATE_URL
            self.ollama_url = default_url
        else:
             self.ollama_url = default_url
             
        if ollama_url: # Se passado no construtor
             self.ollama_url = ollama_url
        self.prompts = self._load_prompts()
        # self.fsm = TicketFSM() # Removido na refatoração Agentic

        
    def _load_prompts(self) -> Dict[str, Any]:
        prompt_path = Path(__file__).parent / "prompts.yaml"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _call_llm(self, system_prompt: str, user_input: str) -> str:
        """Chamada compatível com OpenAI API (vLLM)"""
        # Endpoint: /v1/chat/completions
        # Se LLM_BASE_URL terminar com /v1, usamos ele direto
        base_url = os.getenv("LLM_BASE_URL", "http://host.docker.internal:9000/v1").rstrip('/')
        api_url = f"{base_url}/chat/completions"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.1, # Deterministico
            # "response_format": {"type": "json_object"} # Removido para compatibilidade
        }
        
        try:
            # 120s timeout para garantir
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Erro ao chamar LLM ({api_url}): {e}")
            if 'response' in locals() and response.text:
                print(f"Server Response: {response.text}")
            return "{}"

    def _call_remote_classifier(self, text: str) -> Dict[str, Any]:
        """Consulta o Agente Classificador via API Interna"""
        # URL interna do serviço no Docker
        url = "http://glpi-ai-worker:8002/predict"
        # Se rodando fora do docker (teste local), tentar localhost
        if not os.getenv("KUBERNETES_SERVICE_HOST") and not os.path.exists('/.dockerenv'):
            url = "http://localhost:8002/predict"
            
        try:
            payload = {"summary": text, "description": text}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"🧠 Classificador: {result['category_name']} ({result['confidence']})")
                return result
        except Exception as e:
            print(f"⚠️ Classificador Indisponível: {e}")
        return {}

    def _validate_context(self, ctx: TicketContext):
        """
        Valida se as informações obrigatórias foram preenchidas.
        """
        missing = []
        
        # Regra Simplificada: Localização é sempre útil para TI físico.
        # Se for string vazia ou nula/none, falta info.
        if not ctx.location or ctx.location.lower() in ["null", "none", "não informado"]:
             missing.append("location")

        ctx.missing_info = missing
        
        # Só está pronto se não falta nada E tem os campos base.
        if not missing and ctx.summary and ctx.urgency and ctx.description:
             ctx.ready_to_submit = True
        else:
             ctx.ready_to_submit = False

    def process_ticket(self, user_input: str, current_context: TicketContext = None) -> TicketContext:
        """
        Processa a entrada do usuário utilizando abordagem AGENTIC Pura.
        O LLM decide, o código apenas valida.
        """
        # 1. Recupera ou Cria Contexto
        if current_context is None:
            current_context = TicketContext(original_complaint=user_input)
        
        # Histórico
        current_context.history.append(f"User: {user_input}")

        # [NOVO] Consulta o Cérebro (Classificador) se for início de conversa
        classifier_data = {}
        if not current_context.intent and len(current_context.history) == 1:
            classifier_data = self._call_remote_classifier(user_input)

        # 2. Chama LLM (O Cérebro Principal)
        system_prompt = self.prompts.get("system", "")
        
        # Enriquecer Prompt com a sugestão do Classificador
        if classifier_data.get("category_name"):
            system_prompt += f"\n\nSUGESTÃO DE CATEGORIA: {classifier_data['category_name']}"
        
        # Passar contexto atual COMPLETO para o LLM não se perder
        if current_context.summary or current_context.intent:
            ctx_str = f"""
CONTEXTO ATUAL (O que já sabemos):
- Resumo: {current_context.summary}
- Descrição: {current_context.description}
- Local: {current_context.location}
- Urgência: {current_context.urgency}
- Intenção: {current_context.intent}
            """
            system_prompt += f"\n{ctx_str}"

        # [CORRECAO CRITICA] Injetar Histórico para o Agente ter memória de curto prazo
        # Sem isso, ele esquece que acabou de fazer uma pergunta.
        if current_context.history:
            # Pegamos as últimas 6 mensagens para manter o contexto fresco sem estourar tokens
            recent_history = current_context.history[-6:]
            hist_str = "\n".join(recent_history)
            system_prompt += f"\n\nHISTÓRICO DA CONVERSA (Memória):\n{hist_str}\n"

        # Força o modelo a focar no JSON no final do turno
        final_user_input = f"{user_input}\n\n(Responda APENAS com o JSON)"
        llm_response_str = self._call_llm(system_prompt, final_user_input)
        
        extracted_data = {}
        try:
            # Limpeza básica de Markdown
            clean_text = llm_response_str.replace("```json", "").replace("```", "").strip()
            extracted_data = json.loads(clean_text)
        except Exception as e:
            print(f"Erro parse JSON LLM: {e}. Ignorando atualização estruturada.")
            print(f"Raw Response: {llm_response_str}")
        
        # 3. Atualizar Contexto com dados do LLM (Sem FSM no caminho)
        if extracted_data:
            # Mapeia campos do JSON para o Objeto
            if extracted_data.get("reasoning"): current_context.reasoning = extracted_data["reasoning"]
            if extracted_data.get("summary"): current_context.summary = extracted_data["summary"]
            if extracted_data.get("description"): current_context.description = extracted_data["description"]
            if extracted_data.get("location"): current_context.location = extracted_data["location"]
            if extracted_data.get("urgency"): current_context.urgency = extracted_data["urgency"]
            if extracted_data.get("impact"): current_context.impact = extracted_data["impact"]
            if extracted_data.get("response_to_user"): current_context.response_to_user = extracted_data["response_to_user"]
            
            # Intenção: Classificador > LLM > Anterior
            if classifier_data.get("category_name"):
                 # Simplificação: Usar category_name como intent por enquanto ou mapear
                 pass 
            
            # Se LLM detectou intent e não tínhamos
            if not current_context.intent and extracted_data.get("intent"):
                 current_context.intent = extracted_data["intent"]

        # 4. Validação (Passiva)
        self._validate_context(current_context)
        
        # Adiciona resposta do bot ao histórico
        if current_context.response_to_user:
             current_context.history.append(f"Agent: {current_context.response_to_user}")

        return current_context

    def run(self):
        """Loop simples para teste no terminal"""
        print(">> Agente Opener AGENTIC Iniciado (Sem FSM)")
        ctx = None 
        
        while True:
            user_input = input("\nUsuário: ")
            if user_input.lower() in ["sair", "exit"]:
                break
            
            # Mantém estado entre turnos no loop local
            ctx = self.process_ticket(user_input, current_context=ctx)
            
            if ctx.response_to_user:
                print(f"\n>> Agente: {ctx.response_to_user}")
            
            if ctx.ready_to_submit:
                print("\n>> [SISTEMA] TICKET PRONTO PARA ABERTURA.")
                print(f">> Resumo: {ctx.summary}")
                print(f">> Local: {ctx.location}")
                print(f">> Urgência: {ctx.urgency}")
                # Reset para novo ticket
                ctx = None

if __name__ == "__main__":
    agent = SurgicalOpenerAgent()
    agent.run()
