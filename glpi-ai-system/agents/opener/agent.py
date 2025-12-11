import yaml
import json
import requests
from pathlib import Path
from typing import List, Dict, Any
from .schemas import TicketContext
import os

class SurgicalOpenerAgent:
    def __init__(self, model_name: str = "llama3.1:8b", ollama_url: str = None):
        self.model_name = model_name
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
        
    def _load_prompts(self) -> Dict[str, Any]:
        prompt_path = Path(__file__).parent / "prompts.yaml"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _call_llm(self, system_prompt: str, user_input: str) -> str:
        # Simplificação para chamada via requests (evita dependências complexas)
        full_prompt = f"{system_prompt}\n\nUSER INPUT: {user_input}\n\nRESPONSE (JSON):"
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "format": "json" # Força saída JSON no Ollama
        }
        
        try:
            # Aumentado timeout para 120s para permitir loading do modelo
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "{}")
        except Exception as e:
            print(f"Erro ao chamar LLM: {e}")
            return "{}"

    def process_ticket(self, user_input: str, current_context: TicketContext = None) -> TicketContext:
        """
        Processa a entrada do usuário e retorna o contexto atualizado.
        """
        system_prompt = self.prompts.get("system", "")
        
        start_request_text = user_input
        # Se tivessemos contexto anterior, poderiamos concatenar
        
        llm_response_str = self._call_llm(system_prompt, start_request_text)
        
        try:
            data = json.loads(llm_response_str)
            # Garante que original_complaint esteja presente
            if "original_complaint" not in data:
                data["original_complaint"] = user_input
                
            updated_context = TicketContext(**data)
            
            # Validação Extra: Se não está pronto e não tem pergunta, algo deu errado.
            # O Prompt deveria ter gerado response_to_user. Se falhou, forçamos.
            if not updated_context.ready_to_submit and not updated_context.response_to_user:
                # Fallback: Se não sei o que fazer, pergunto algo genérico técnico
                updated_context.response_to_user = "Pode me dar mais detalhes técnicos sobre o problema?"
            
            # Lógica simples de verificação de preenchimento (se o LLM acertou os slots mas esqueceu a flag)
            if updated_context.urgency and updated_context.impact and updated_context.location and updated_context.summary:
                updated_context.ready_to_submit = True
            
            return updated_context
            
        except Exception as e:
            print(f"Erro no processamento (LLM ou Validação): {e}")
            # Fallback seguro
            return TicketContext(
                original_complaint=user_input, 
                response_to_user="Desculpe, tive um erro técnico interno. Pode repetir?"
            )

    def run(self):
        """Loop simples para teste no terminal"""
        print(">> Agente Opener Iniciado (Digite 'sair' para encerrar)")
        while True:
            user_input = input("\nUsuário: ")
            if user_input.lower() in ["sair", "exit"]:
                break
            
            ctx = self.process_ticket(user_input)
            print(f"\n>> Agente (JSON Interno): {ctx.model_dump_json(indent=2)}")
            
            if ctx.response_to_user:
                print(f"\n>> Agente: {ctx.response_to_user}")
            
            if ctx.ready_to_submit:
                print("\n>> [SISTEMA] TICKET PRONTO PARA ABERTURA.")
                # Aqui poderia chamar a API do GLPI real se fosse o caso
                break

if __name__ == "__main__":
    agent = SurgicalOpenerAgent()
    agent.run()
