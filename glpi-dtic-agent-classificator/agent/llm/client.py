
import json
import logging
from typing import Dict, Any, Optional
import httpx

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from .config import LLMConfig

# Configure module-level logger
logger = logging.getLogger("LLMClient")

class LLMClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model_name: Optional[str] = None, timeout: Optional[int] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        self.provider = LLMConfig.PROVIDER
        if self.provider == "ollama":
            self.base_url = LLMConfig.OLLAMA_URL
        else:
            self.base_url = base_url or LLMConfig.BASE_URL
        self.api_key = api_key or LLMConfig.API_KEY
        self.model_name = model_name or LLMConfig.MODEL_NAME
        self.timeout = timeout or LLMConfig.TIMEOUT_SECONDS
        self.temperature = temperature if temperature is not None else LLMConfig.TEMPERATURE
        self.max_tokens = max_tokens or LLMConfig.MAX_TOKENS
        logger.info(f"Connecting to LLM provider={self.provider} at {self.base_url} (Model: {self.model_name})")
        if self.provider == "openai":
            if not HAS_OPENAI:
                logger.error("Library 'openai' not found. Please install: pip install openai")
                raise ImportError("Missing 'openai' dependency")
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key, timeout=self.timeout)
        else:
            self.http = httpx.Client(timeout=self.timeout)

    def completion_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Sends a prompt to the LLM and expects a JSON response.
        Retries logic could be added here.
        """
        try:
            sys_prompt = system_prompt
            for attempt in range(2):
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=self.temperature,
                        response_format={"type": "json_object"},
                        max_tokens=self.max_tokens
                    )
                    content = response.choices[0].message.content
                else:
                    payload = {
                        "model": self.model_name,
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "options": {
                            "temperature": self.temperature
                        },
                        "stream": False
                    }
                    r = self.http.post(f"{self.base_url}/api/chat", json=payload)
                    r.raise_for_status()
                    data = r.json()
                    content = data.get("message", {}).get("content", "")

                try:
                    data = json.loads(content)
                    return data
                except json.JSONDecodeError:
                    start = content.find('{')
                    end = content.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        snippet = content[start:end+1]
                        try:
                            data = json.loads(snippet)
                            return data
                        except Exception:
                            pass
                    lower = content.lower()
                    for key in ("correct", "incorrect", "suspect"):
                        if key in lower:
                            return {"status": key, "reason": content[:200]}
                    if attempt == 0:
                        sys_prompt = sys_prompt + "\nResponda SOMENTE com um objeto JSON válido sem markdown ou texto adicional."
                    else:
                        logger.warning(f"Failed to parse JSON from LLM response: {content[:100]}...")
                        return None

        except Exception as e:
            logger.error(f"LLM Request Failed: {e}")
            return None
            
    def check_health(self) -> bool:
        """Simple ping to check if LLM is responsive"""
        try:
            if self.provider == "openai":
                self.client.models.list()
            else:
                r = self.http.get(f"{self.base_url}/api/tags")
                r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Health Check Failed: {e}")
            return False
