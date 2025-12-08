import os
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConnector:
    """
    Connects to a local Ollama instance to perform intelligent classification.
    """
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        self.model = os.getenv("LLM_MODEL_NAME", "llama3") # Default to generic llama3 if env not set
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.api_chat_endpoint = f"{self.base_url}/api/chat"
        
        # Validate connection on init? Or lazy? Let's do lazy to keep it lightweight.
        print(f"[LLMConnector] Initialized. Target: {self.base_url} | Model: {self.model}")

    def chat_completion(self, messages: List[Dict]) -> str:
        """
        Sends a conversation history to the model and returns the response content.
        Args:
            messages: List of dicts, e.g. [{"role": "user", "content": "..."}]
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7  # Higher temperature for more natural conversation
            }
        }
        
        try:
            response = requests.post(self.api_chat_endpoint, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            # Ollama API structure for chat: result['message']['content']
            return result.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            print(f"[LLMConnector] Chat Error: {e}")
            return "Desculpe, ocorreu um erro de conexão com o Agente."

    def decide_category(self, ticket_text: str, options: List[str]) -> Dict[str, str]:
        """
        Asks the LLM to choose the best category from the provided options.
        Returns a dictionary with 'category' and 'reason'.
        """
        
        # Construct a clear, strict prompt
        options_str = "\n".join([f"- {opt}" for opt in options])
        
        prompt = f"""
        You are an IT Service Desk Expert.
        
        TICKET DESCRIPTION:
        "{ticket_text}"
        
        AVAILABLE CATEGORIES:
        {options_str}
        
        TASK:
        Select the SINGLE BEST category for this ticket from the list above.
        Use your reasoning skills. For example, "Installing a computer" is Hardware, not Software.
        
        OUTPUT FORMAT:
        Respond ONLY with a valid JSON object in this format:
        {{
            "category": "Exact Category Name From List",
            "reason": "Brief explanation of why"
        }}
        Do not write anything else.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json", # Enforce JSON mode if model supports it (Llama 3 usually does)
            "options": {
                "temperature": 0.1 # Low temperature for consistent, deterministic answers
            }
        }

        try:
            response = requests.post(self.api_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Parse JSON from LLM response
            try:
                decision = json.loads(response_text)
                return decision
            except json.JSONDecodeError:
                # Fallback if LLM didn't return pure JSON (rare with json mode but possible)
                print(f"[LLMConnector] ERROR: Could not parse JSON. Raw: {response_text}")
                return {"category": "Error", "reason": "Invalid JSON response"}
                
        except requests.exceptions.RequestException as e:
            print(f"[LLMConnector] Connection Error: {e}")
            return {"category": "Error", "reason": "Connection failed"}

if __name__ == "__main__":
    # Internal Test
    print(">>> Testing LLMConnector...")
    
    connector = LLMConnector()
    
    # Test Case: The exact ambiguity we faced
    test_ticket = "Instalação de computador e monitores em substituição aos existentes."
    test_options = [
        "1. Hardware e Impressão > Periféricos",
        "1. Hardware e Impressão > Computadores e Notebooks",
        "1. Hardware e Impressão > Instalação de Equipamentos",
        "3. Software e Sistemas > Outros Softwares > Instalação de Software",
        "3. Software e Sistemas > Configuração de Software"
    ]
    
    print(f"\nTicket: {test_ticket}")
    print("Options:")
    for opt in test_options:
        print(f" - {opt}")
        
    print("\nRequesting LLM decision...")
    result = connector.decide_category(test_ticket, test_options)
    
    print("\n>>> RESULTADO:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Simple validation
    if result.get("category") == "1. Hardware e Impressão > Instalação de Equipamentos":
        print("\n✅ TEST PASSED: LLM correctly identified Hardware Installation.")
    else:
        print("\n❌ TEST FAILED: LLM chose incorrectly.")
