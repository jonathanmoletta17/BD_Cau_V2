import httpx
import json
from src.config import settings
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class LLMService:
    def __init__(self, model: str = None):
        self.base_url = settings.INFERENCE_SERVER_URL
        self.model = model or settings.LLM_MODEL
        logger.info(f"LLM Service Initialized with Model: {self.model} | Base URL: {self.base_url}")

    async def generate_response(self, prompt: str, system_prompt: str = None, temperature: float = 0.0) -> str:
        """
        Legacy method for single prompt generation.
        """
        return await self.chat_completion([
            {"role": "system", "content": system_prompt or ""},
            {"role": "user", "content": prompt}
        ], options={"temperature": temperature})

    async def chat_completion(self, messages: list, options: dict = None) -> str:
        """
        Calls Ollama Chat API.
        Endpoint: POST /api/chat
        """
        url = f"{self.base_url}/api/chat"
        
        valid_messages = [m for m in messages if m.get("content")]

        default_options = {
            "temperature": 0.3, 
        }
        if options:
            default_options.update(options)

        payload = {
            "model": self.model,
            "messages": valid_messages,
            "stream": False,
            "options": default_options
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"Calling LLM Chat with {len(messages)} messages")
                response = await client.post(url, json=payload, timeout=60.0) # Increased timeout
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
        except httpx.HTTPError as e:
            logger.error(f"LLM Chat generation failed: {e}")
            raise
