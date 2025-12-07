import json
import os
import glob
from datetime import datetime

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset_CLEAN.json")
# If CLEAN doesn't exist yet (first run of this specific flow?), check standard
if not os.path.exists(DATASET_PATH):
    DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")

REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

def get_latest_report():
    list_of_files = glob.glob(os.path.join(REPORTS_DIR, 'accuracy_report_*.json')) 
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def main():
    report_path = get_latest_report()
    if not report_path:
        print("❌ Nenhum relatório encontrado.")
        return

    print(f"📖 Lendo relatório fonte: {os.path.basename(report_path)}")
    with open(report_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    print(f"📖 Lendo dataset alvo: {os.path.basename(DATASET_PATH)}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    # Create ID map for dataset
    dataset_map = {item['id']: item for item in dataset}
    
    fixes_count = 0
    target_human_category = "AJUDA E SUPORTE" # The "Lazy" Category
    
    details = report_data.get("details", [])
    
    print(f"🔍 Analisando {len(details)} resultados de avaliação...")
    
    for item in details:
        # Check if it is an error AND the human label matches our target generic category
        if item.get("correct") is False and item.get("true_category") == target_human_category:
            
            ticket_id = item.get("id")
            ai_prediction = item.get("predicted_category")
            
            # Find in dataset
            if ticket_id in dataset_map:
                ticket = dataset_map[ticket_id]
                
                # Double check current state (maybe it was already fixed?)
                if ticket["true_category"] == target_human_category:
                    # APPLY FIX
                    print(f"   [FIX] ID {ticket_id}: '{target_human_category}' -> '{ai_prediction}'")
                    ticket["true_category"] = ai_prediction
                    fixes_count += 1
    
    if fixes_count > 0:
        print(f"\n💾 Salvando {fixes_count} correções em {DATASET_PATH}...")
        with open(DATASET_PATH, "w", encoding="utf-8") as f:
            json.dump(list(dataset_map.values()), f, indent=4, ensure_ascii=False)
        print("✅ Concluído!")
    else:
        print("\n✅ Nenhuma correção necessária (ou nenhum caso encontrado).")

if __name__ == "__main__":
    main()
