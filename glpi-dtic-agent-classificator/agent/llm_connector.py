import os
import json
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConnector:
    """
    Connects to a local LLM (Ollama or Nvidia NIM) using OpenAI-compatible API.
    """
    def __init__(self):
        # Support both Ollama and NIM via generic config
        self.base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
        
        # FIX: If running locally (Host), 'host.docker.internal' won't resolve. Replace with localhost.
        # We assume if we can't resolve it, we are on host. Or just simple string replace if not inside docker?
        # A simple check: os.path.exists('/.dockerenv') usually indicates docker.
        if "host.docker.internal" in self.base_url and not os.path.exists('/.dockerenv'):
             print("[LLMConnector] Local environment detected. Switching host.docker.internal -> localhost")
             self.base_url = self.base_url.replace("host.docker.internal", "localhost")
        
        self.api_key = os.getenv("LLM_API_KEY", "dummy")
        self.model = os.getenv("LLM_MODEL_NAME", "llama3.1:8b") 
        
        self.api_endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        
        print(f"[LLMConnector] Initialized. Endpoint: {self.api_endpoint} | Model: {self.model}")

    def _send_request(self, messages: List[Dict], temperature: float = 0.7, json_mode: bool = False) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(self.api_endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            # Standard OpenAI Response Structure
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"[LLMConnector] API Error: {e}")
            if e.response:
                print(f"Details: {e.response.text}")
            return ""
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[LLMConnector] Parse Error: {e}")
            return ""

    def chat_completion(self, messages: List[Dict]) -> str:
        """Sequential Chat Inteface"""
        return self._send_request(messages, temperature=0.7)

    def decide_category(self, ticket_text: str, options: List[str]) -> Dict[str, str]:
        """Categorization Logic"""
        
        options_str = "\n".join([f"- {opt}" for opt in options])
        
        system_prompt = f"""You are an IT Service Desk Expert.
        Select the SINGLE BEST category for the ticket from the list below.
        
        AVAILABLE CATEGORIES:
        {options_str}
        
        OUTPUT FORMAT:
        Respond ONLY with a valid JSON object:
        {{
            "category": "Exact Category Name",
            "reason": "Brief explanation"
        }}"""
        
        user_prompt = f"TICKET DESCRIPTION:\n{ticket_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_text = self._send_request(messages, temperature=0.1, json_mode=True)
        
        if not response_text:
             return {"category": "Error", "reason": "No response from LLM"}

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            print(f"[LLMConnector] Failed to parse JSON: {response_text}")
            return {"category": "Error", "reason": "Invalid JSON"}

    def service_desk_dialog(self, history: List[Dict], categories: List[str]) -> str:
        """
        Generates the next response in the Service Desk conversation.
        history: List of {"role": "user"/"assistant", "content": "..."}
        categories: List of valid GLPI category names.
        
        Returns: 
           - A text string (question/clarification) to send to the user.
           - OR a JSON string if the ticket is ready to be created.
        """
        categories_str = ", ".join(categories)
        
        system_prompt = f"""You are a helpful IT Service Desk Assistant linked to GLPI.
        Your goal is to collect information to open a support ticket.
        
        REQUIRED INFORMATION:
        1. Description of the problem (Clear and detailed).
        2. Category (Must be one of: {categories_str}).
        3. Urgency (High/Medium/Low).
        4. Impact (High/Medium/Low).
        5. User Email (Required for identification).
        
        INSTRUCTIONS:
        - Converse naturally with the user in Portuguese (Brazil).
        - DO NOT INVENT DETAILS. Use ONLY information provided by the user.
        - If information is missing (including Email), ask clarifying questions.
        - DO NOT ask for everything at once. Be polite.
        - Infer Category, Urgency, and Impact from context if possible.
        
        CRITICAL: 
        - DO NOT generate the JSON ticket until you have Description AND Email.
        
        FINAL OUTPUT FORMAT:
        WHEN you have all 5 pieces of information:
        OUTPUT A SINGLE JSON OBJECT like this:
        {{
            "action": "create_ticket",
            "title": "Short title",
            "description": "Full description",
            "category": "Exact Category Name",
            "urgency": "High" | "Medium" | "Low",
            "impact": "High" | "Medium" | "Low",
            "email": "user@email.com"
        }}
        """
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        # We allow a bit more creativity (temperature 0.3) but still focused
        return self._send_request(messages, temperature=0.3)
