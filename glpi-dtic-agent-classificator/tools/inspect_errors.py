import json
import os
import glob

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    print(f"📖 Lendo relatório: {os.path.basename(report_path)}")
    
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Load dataset to get text
    dataset_path = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset_CLEAN.json")
    text_map = {}
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            ds = json.load(f)
            text_map = {item["id"]: item["text"] for item in ds}

    # Filter for "AJUDA E SUPORTE" errors
    target_category = "AJUDA E SUPORTE"
    
    output_file = os.path.join(PROJECT_ROOT, "data", "error_inspection.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"🔍 Analisando erros onde a categoria (Humana ou IA) envolve: '{target_category}'\n\n")

        count = 0
        all_items = data.get("details", [])
                
        for item in all_items:
            if item.get("correct") is True:
                continue

            human = item["true_category"]
            ai = item["predicted_category"]
            
            # We want to see cases where one of them is the generic category
            # to understand the confusion.
            if (human == target_category or ai == target_category) and human != ai:
                count += 1
                tid = item['id']
                text = text_map.get(tid, "Texto não encontrado")
                
                f.write(f"--- Erro #{count} ---\n")
                f.write(f"🆔 ID: {tid}\n")
                f.write(f"Previsão: {ai} | Real: {human}\n")
                f.write(f"📝 Texto: {text}\n")
                f.write("-" * 50 + "\n")
                
                if count >= 50: # Increased limit
                    break
        
        f.write(f"\nTotal visualizado: {count}\n")
    
    print(f"✅ Análise salva em: {output_file}")

if __name__ == "__main__":
    main()
