import json
import yaml
import re

def clean_key(key):
    # Gera um ID curto baseado nas iniciais ou lógica simples
    # Ex: "1. Hardware e Impressão" -> "hardware_impressao"
    clean = key.lower().replace(" > ", "_").replace(" ", "_").replace("/", "").replace(".", "")
    clean = re.sub(r'_+', '_', clean)
    return clean[:30]

def convert():
    with open('category_context.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    taxonomy = []
    
    for category_path, keywords in data.items():
        # Separa a hierarquia para criar metadados se necessário
        parts = category_path.split(' > ')
        main_category = parts[0]
        
        # Cria o objeto estruturado
        item = {
            "id": clean_key(category_path),
            "name": category_path.strip(),
            "description": keywords.strip(),
            "keywords": keywords.strip(), # Neste caso simples, keywords = description
            # Formato específico para o modelo de embedding sugerido (SBERT best practice)
            "embedding_source": f"passage: {category_path}: {keywords}" 
        }
        taxonomy.append(item)

    # Ordena pelo nome para ficar organizado
    taxonomy.sort(key=lambda x: x['name'])

    # Salva em glpi-ai-system/agents/classifier/taxonomy.yaml
    output_path = 'glpi-ai-system/agents/classifier/taxonomy.yaml'
    
    # Garante que o diretório existe (se rodarmos dentro do script, mas idealmente o agente cria)
    # Por enquanto vou salvar na raiz para mover depois ou direto se a pasta existir
    import os
    os.makedirs('glpi-ai-system/agents/classifier', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(taxonomy, f, allow_unicode=True, sort_keys=False)
    
    print(f"Convertido {len(taxonomy)} categorias para {output_path}")

if __name__ == "__main__":
    convert()
