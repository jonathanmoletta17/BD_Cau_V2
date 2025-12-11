import yaml
import json
import requests
from pathlib import Path
from typing import List, Dict, Any
from .schemas import TicketContext
import os

from .fsm_standalone import TicketFSM

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
        self.fsm = TicketFSM() # Inicializa o cérebro de regras
        
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
        Processa a entrada do usuário utilizando FSM Híbrida (Regras + LLM).
        """
        # 1. Recupera ou Cria Contexto
        if current_context is None:
            current_context = TicketContext(original_complaint=user_input)
            
        # 2. Chama LLM para extração "inteligente" (Intent, Entities)
        # O LLM atua agora como um "Parser Semântico", não como o decisor final.
        system_prompt = self.prompts.get("system", "")
        llm_response_str = self._call_llm(system_prompt, user_input)
        
        extracted_data = {}
        try:
            extracted_data = json.loads(llm_response_str)
        except Exception as e:
            print(f"Erro parse JSON LLM: {e}. Usando fallback FSM puro.")
        
        # 3. Passa a bola para a FSM (O Cérebro)
        # A FSM recebe o input bruto E o que o LLM achou.
        # Ela decide se acredita no LLM, aplica regras rígidas e atualiza o contexto.
        updated_context = self.fsm.process_input(current_context, user_input, llm_data=extracted_data)
        
        return updated_context

    def run(self):
        """Loop simples para teste no terminal"""
        print(">> Agente Opener HÍBRIDO Iniciado (FSM + LLM)")
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
