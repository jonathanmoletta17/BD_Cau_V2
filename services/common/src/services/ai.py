
import os
import requests
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class OllamaService:
    """
    Service to interact with Ollama/NIM API for generating embeddings.
    Designed to be 'Fail Soft' - if AI is down, it logs and returns None instead of crashing.
    """
    def __init__(self, base_url: str = None, embedding_model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://nim-llm:8000") # Default to internal docker name
        self.embedding_model = embedding_model or os.getenv("OLLAMA_EMBED_MODEL", "nvidia/nv-embedqa-e5-v5")
        
        # Normalize URL
        self.base_url = self.base_url.rstrip('/')

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for the given text.
        Returns None if service is unreachable or errors.
        """
        if not text or not text.strip():
            return None

        url = f"{self.base_url}/v1/embeddings" # OpenAI compatible endpoint standard for NIM/Ollama
        
        # Payload designed for OpenAI-compatible API (standard for NIM & newer Ollama)
        payload = {
            "input": text,
            "model": self.embedding_model,
            "encoding_format": "float"
        }
        
        # Fallback for raw Ollama API (if /v1/ fails or configured differently)
        # But let's stick to one standard first or try/except?
        # Nomic/Ollama native: POST /api/embeddings {model, prompt}
        # NIM/OpenAI: POST /v1/embeddings {model, input}
        
        try:
            # Try Standard OpenAI format first (NIM default)
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 404:
                # Fallback to pure Ollama API
                 return self._get_embedding_ollama_raw(text)
                 
            response.raise_for_status()
            data = response.json()
            
            # OpenAI format response: data=[{embedding: [...]}]
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0]['embedding']
                
            return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ AI Service Unreachable ({self.base_url}): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ AI Embedding Error: {e}")
            return None

    def _get_embedding_ollama_raw(self, text: str) -> Optional[List[float]]:
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.embedding_model,
            "prompt": text
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding")
        except Exception as e:
            logger.warning(f"⚠️ AI Service (Raw) Unreachable: {e}")
            return None
