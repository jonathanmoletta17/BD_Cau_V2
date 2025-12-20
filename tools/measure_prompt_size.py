import json
import os
import sys

# Add project root to path to find other modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def estimate_tokens(text):
    """
    Estimates token count.
    Llama 3 tokenizer is roughly 1 token per 3-4 characters for English,
    but for Portuguese/Code it might be denser.
    We will use a conservative 1 token = 3 characters estimate.
    """
    try:
        import tiktoken
        # cl100k_base is for GPT-4, but it's a decent proxy for modern BPE tokenizers
        enc = tiktoken.get_encoding("cl100k_base") 
        return len(enc.encode(text))
    except ImportError:
        # Fallback
        return len(text) // 3

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../agents/local_triage/intents_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {config_path}")
        return {}

def measure_classification_prompt(config):
    categories_text = ""
    for intent_name, data in config.items():
        categories_text += f"- {intent_name} ({data['description']})\n    "
    
    system_prompt = f"""Você é um classificador preciso. 
    Classifique a entrada do usuário em UMA destas categorias: 
    {categories_text}
    
    Responda APENAS com o nome da categoria. Não explique."""
    
    return estimate_tokens(system_prompt)

def measure_extraction_prompts(config):
    results = {}
    for intent_name, data in config.items():
        fields_config = data.get('fields', [])
        examples_list = data.get('examples', [])
        
        instructions_str = ""
        for f in fields_config:
            instructions_str += f"- {f['name']}: {f['instruction']}\n"

        examples_str = ""
        if examples_list:
            examples_str = "\nEXEMPLOS DE COMO EXTRAIR:\n" + "\n".join(examples_list)
            
        prompt = f"""Extraia as informações...
        {instructions_str}
        {examples_str}
        """
        results[intent_name] = estimate_tokens(prompt)
    return results

def main():
    print("--- LLM Load Estimator ---")
    config = load_config()
    if not config:
        return

    print(f"Loaded {len(config)} intents.")
    
    # 1. Classification Load
    class_tokens = measure_classification_prompt(config)
    print(f"\n[Classification Phase]")
    print(f"System Prompt Size: ~{class_tokens} tokens")
    print(f"Context Limit (Default): 2048 tokens")
    print(f"Context Limit (New): 8192 tokens")
    usage_pct = (class_tokens / 8192) * 100
    print(f"Load on 8k Context: {usage_pct:.1f}% (Very Safe)")
    
    # 2. Extraction Load (Worst Case)
    extract_counts = measure_extraction_prompts(config)
    max_intent = max(extract_counts, key=extract_counts.get)
    max_tokens = extract_counts[max_intent]
    
    print(f"\n[Extraction Phase - Worst Case]")
    print(f"Heaviest Intent: {max_intent} (~{max_tokens} tokens)")
    print(f"Load on 8k Context: {(max_tokens / 8192) * 100:.1f}%")

    print("\n--- Recommendation ---")
    if class_tokens > 1500:
        print("WARNING: Classification prompt is getting large. Consider splitting intents.")
    elif max_tokens > 1500:
        print(f"WARNING: Intent '{max_intent}' has too many examples/fields. Reduce them.")
    else:
        print("All prompts are well within safe limits for Llama 3.1 8B (especially with 8k context).")

if __name__ == "__main__":
    main()
