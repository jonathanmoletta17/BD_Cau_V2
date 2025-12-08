import argparse
import json
import sys
import os

# Add current directory to path so we can import tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agent.llm.client import LLMClient
from agent.llm.prompts import CuratorPrompts

def main():
    parser = argparse.ArgumentParser(description="Teste simples do Agente Classificador")
    parser.add_argument("--title", required=True, help="Titulo do ticket")
    parser.add_argument("--desc", required=True, help="Descricao do ticket")
    parser.add_argument("--cat", required=True, help="Categoria atual")
    
    args = parser.parse_args()
    
    print(f"--- Iniciando Verificacao ---")
    print(f"Ticket: {args.title}")
    print(f"Categoria: {args.cat}")
    print("Conectando ao Ollama...")

    # 1. Inicializa Cliente
    llm = LLMClient()
    
    # 2. Prepara Prompt
    prompt_user = CuratorPrompts.BINARY_JUDGE_USER_TEMPLATE.format(
        title=args.title, 
        description=args.desc, 
        current_category=args.cat
    )
    
    # 3. Envia
    result = llm.completion_json(CuratorPrompts.BINARY_JUDGE_SYSTEM, prompt_user)
    
    # 4. Mostra Resultado
    print("\n--- Resultado ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
