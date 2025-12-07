"""
Script para Buscar Dados de Validação do GLPI
============================================

PROPÓSITO:
    Busca tickets já categorizados no GLPI para expandir o dataset de validação.
    Evita duplicatas e foca em tickets que já possuem uma 'true_category'.

USO:
    python tools/fetch_validation_data.py [--limit 500]
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Set

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glpi_agent.glpi_client import GlpiClient
from glpi_agent.preprocess import join_title_description

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("FetchData")

# Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")

def load_existing_dataset() -> List[Dict]:
    if not os.path.exists(DATASET_PATH):
        return []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_dataset(data: List[Dict]) -> None:
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Busca tickets categorizados do GLPI.")
    parser.add_argument("--limit", type=int, default=500, help="Máximo de tickets a buscar por vez")
    args = parser.parse_args()

    logger.info("🎬 Iniciando busca de dados de validação...")

    # 1. Carrega dataset existente para evitar duplicatas
    existing_data = load_existing_dataset()
    existing_ids = {item["id"] for item in existing_data}
    logger.info(f"Dataset atual: {len(existing_data)} tickets.")

    # 2. Conecta ao GLPI
    client = GlpiClient(environment="test") # Usar test ou prod conforme disponibilidade
    client.init_session()
    
    if not client.session_token:
        logger.error("❌ Falha na autenticação com GLPI.")
        sys.exit(1)
    
    logger.info("✅ Conectado ao GLPI.")

    # 3. Busca categorias para mapear ID -> Nome
    logger.info("Mapeando categorias...")
    cat_map_name_to_id = client.categories_map()
    cat_id_to_name = {v: k for k, v in cat_map_name_to_id.items()}
    logger.info(f"Mapeadas {len(cat_id_to_name)} categorias.")

    # 4. Busca tickets categorizados
    # Nota: A API do GLPI pode não suportar filtros complexos no search_items simples,
    # então buscamos tickets não deletados e filtramos localmente ou usamos range.
    logger.info(f"Buscando últimos {args.limit} tickets...")
    
    # Busca um range maior para garantir que encontremos categorizados
    # O client.list_categorized_tickets já filtra, mas pode ser lento se trouxer tudo.
    # Vamos usar search_items com sort descrescente se possível, ou apenas pegar um range grande.
    
    # Estratégia: Pegar tickets recentes (por ID decrescente seria ideal, mas a API padrão lista ascending)
    # Vamos pegar um range grande de itens recentes.
    # list_items_range usa range=0-limit.
    
    raw_tickets = client.search_items("Ticket", {"is_deleted": "0", "sort": "id", "order": "DESC", "range": f"0-{args.limit}"})
    
    if not raw_tickets:
        logger.warning("Nenhum ticket encontrado.")
        return

    logger.info(f"Analisando {len(raw_tickets)} tickets retornados...")

    new_count = 0
    
    for t in raw_tickets:
        tid = t.get("id")
        
        # Pula se já existe
        if tid in existing_ids:
            continue
            
        # Pula se não tem categoria
        cat_id = t.get("itilcategories_id")
        if cat_id in (0, "0", None, ""):
            continue
            
        # Pula se a categoria não está no mapa (pode estar inativa ou excluída)
        # Tenta converter para int para garantir match
        try:
            cat_id_int = int(cat_id)
        except ValueError:
            continue
            
        true_category = cat_id_to_name.get(cat_id_int)
        if not true_category:
            continue

        # Prepara o item do dataset
        text = join_title_description(t.get("name", ""), t.get("content", ""))
        
        # Limpeza básica se necessário (opcional, o join já limpa HTML tags)
        
        item = {
            "id": tid,
            "text": text,
            "true_category": true_category
        }
        
        existing_data.append(item)
        existing_ids.add(tid)
        new_count += 1

    # 5. Salva resultado
    if new_count > 0:
        save_dataset(existing_data)
        logger.info(f"✅ Adicionados {new_count} novos tickets ao dataset.")
        logger.info(f"Total agora: {len(existing_data)} tickets.")
    else:
        logger.info("⏹️ Nenhum ticket novo relevante encontrado.")

if __name__ == "__main__":
    main()
