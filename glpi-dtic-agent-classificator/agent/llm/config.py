
# Configuration for LLM Curator
import os
from dotenv import load_dotenv

# Load environment variables from the root .env file
# Assuming this script is run from a context where .env is accessible or loaded
load_dotenv()

class LLMConfig:
    BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
    MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3.1:8b")
    BASE_URL_1 = os.getenv("LLM_BASE_URL_1", BASE_URL)
    BASE_URL_2 = os.getenv("LLM_BASE_URL_2", BASE_URL)
    MODEL_NAME_1 = os.getenv("LLM_MODEL_NAME_1", MODEL_NAME)
    MODEL_NAME_2 = os.getenv("LLM_MODEL_NAME_2", MODEL_NAME)
    
    # Inference Parameters
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
    TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT", "60"))
    LOG_FORMAT = os.getenv("LLM_LOG_FORMAT", "json")
    PRIORITY_LEVEL = os.getenv("LLM_PRIORITY_LEVEL", "sequential")
    INPUT_FORMAT = os.getenv("LLM_INPUT_FORMAT", "json")
    MOCK_MODE = os.getenv("LLM_MOCK", "0") == "1"
    PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

    # Processing limits
    BATCH_SIZE = int(os.getenv("LLM_BATCH_SIZE", "1"))

    @staticmethod
    def print_config():
        print("--- LLM Configuration ---")
        print(f"URL: {LLMConfig.BASE_URL}")
        print(f"Model: {LLMConfig.MODEL_NAME}")
        print(f"Temp: {LLMConfig.TEMPERATURE}")
        print("-------------------------")
