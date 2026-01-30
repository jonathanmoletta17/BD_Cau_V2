import httpx
from typing import List
import os

class OllamaService:
    def __init__(self):
        # Allow override for docker internal host if needed
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.embedding_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using Ollama.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
            except Exception as e:
                print(f"Error generating embedding: {e}")
                raise e

    def get_embedding_sync(self, text: str) -> List[float]:
        """
        Generate embedding for the given text (Synchronous).
        """
        import httpx
        with httpx.Client() as client:
            try:
                response = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["embedding"]
            except Exception as e:
                print(f"Error generating embedding (Sync): {e}")
                # Don't crash the sync, just return empty? Or raise?
                # Raising ensures we know it failed.
                raise e

# Global instance
ollama_service = OllamaService()
