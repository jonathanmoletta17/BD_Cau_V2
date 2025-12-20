
import asyncio
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Verify if we can connect to Ollama
llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://host.docker.internal:9000/v1") 
# Try generic localhost if docker internal fails, or assume run from HOST (windows)
# Since I am running this via 'run_command' on Windows, I should use localhost:9000 (if port forwarded) or localhost:11434 ?
# The docker-compose says: LLM_BASE_URL=http://host.docker.internal:9000/v1
# So on the HOST machine, it is likely running on port 9000 (if using LocalAI) or 11434 (Standard Ollama).
# The user said "Heavyweight LLM ... Ollama". Usually 11434.
# I will try 11434 first.

async def test_semantic_understanding():
    print("--- semantic Validation Research (Connecting to Local LLM) ---")
    
    # We try to connect to localhost:11434 first
    try:
        llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://localhost:11434")
        res = llm.invoke("Hello")
        print("Connected to Ollama on 11434.")
    except:
        print("Could not connect to localhost:11434. Trying port 9000...")
        try:
           llm = ChatOllama(model="llama3.1", temperature=0, base_url="http://localhost:9000/v1")
           res = llm.invoke("Hello")
        except Exception as e:
           print(f"Failed to connect to LLM: {2}. Cannot run live research.")
           return

    # Scenario: Field "justificativa" for "EQUIPMENT_REQUEST" (Notebook)
    
    inputs = ["Home Office", "Porque eu quero", "Pizza de Calabresa", "Meu computador quebrou"]
    
    system_prompt = """
    Você é um Validador Semântico.
    Seu trabalho é verificar se a RESPOSTA do usuário faz sentido para a PERGUNTA feita.
    
    Contexto: O usuário está pedindo um Notebook novo.
    Pergunta: Qual é a justificativa da solicitação?
    
    Regras:
    - Responda 'VALID' se a resposta for uma razão lógica (trabalho, defeito, necessidade).
    - Responda 'INVALID' se a resposta for sem sentido, aleatória ou não responder a pergunta.
    """
    
    print("\n--- Testing Inputs ---")
    for user_input in inputs:
        msg = f"Resposta do Usuário: '{user_input}'"
        print(f"\nInput: {user_input}")
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=msg)
        ])
        print(f"Result: {response.content}")

if __name__ == "__main__":
    asyncio.run(test_semantic_understanding())
