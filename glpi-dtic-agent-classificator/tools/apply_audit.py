import json
import os
import shutil

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")
DECISIONS_PATH = os.path.join(PROJECT_ROOT, "data", "audit_decisions.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset_CLEAN.json")

def main():
    print(f"🔄 Iniciando aplicação da auditoria...")
    
    # 1. Load Original Data
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset original não encontrado: {DATASET_PATH}")
        return
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    print(f"📦 Dataset original carregado: {len(dataset)} registros")

    # 2. Load Decisions
    if not os.path.exists(DECISIONS_PATH):
        print(f"⚠️ Nenhuma decisão de auditoria encontrada em: {DECISIONS_PATH}")
        return
    with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
        decisions = json.load(f)
    print(f"⚖️ Decisões de auditoria carregadas: {len(decisions)} registros")

    # 3. Create Decision Map (ID -> Final Category)
    decision_map = {d["id"]: d["final_category"] for d in decisions}

    # 4. Apply Changes
    modified_count = 0
    clean_dataset = []

    for item in dataset:
        ticket_id = item.get("id")
        
        # If we have a decision for this ticket, apply it
        if ticket_id in decision_map:
            new_cat = decision_map[ticket_id]
            old_cat = item.get("true_category")
            
            if new_cat != old_cat:
                item["true_category"] = new_cat
                modified_count += 1
                
        clean_dataset.append(item)

    # 5. Save Clean Dataset
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_dataset, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Concluído! Dataset limpo salvo em:\n   {OUTPUT_PATH}")
    print(f"\n📊 Resumo:")
    print(f"   - Total de Tickets: {len(clean_dataset)}")
    print(f"   - Tickets Auditados: {len(decisions)}")
    print(f"   - Categorias Corrigidas: {modified_count}")
    print(f"   - Mantidos (Decisão Humana ou Sem Mudança): {len(decisions) - modified_count}")

if __name__ == "__main__":
    main()
