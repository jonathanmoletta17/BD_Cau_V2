import json
import os
import shutil

# Configuration
CONFIDENCE_THRESHOLD = 0.80

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")
QUEUE_PATH = os.path.join(PROJECT_ROOT, "data", "audit_queue.json")
DECISIONS_PATH = os.path.join(PROJECT_ROOT, "data", "audit_decisions.json")

OUTPUT_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset_CLEAN.json")
OUTPUT_QUEUE_PATH = os.path.join(PROJECT_ROOT, "data", "audit_queue_filtered.json") # New queue for manual review

def main():
    print(f"🚀 Iniciando Auto-Cleaning (Threshold: {CONFIDENCE_THRESHOLD*100}%)")

    # 1. Load Files
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    audit_queue = []
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            audit_queue = json.load(f)
            
    decisions = []
    if os.path.exists(DECISIONS_PATH):
        with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
            decisions = json.load(f)

    print(f"   - Dataset Original: {len(dataset)}")
    print(f"   - Discrepâncias na Fila: {len(audit_queue)}")
    print(f"   - Decisões Manuais Já Feitas: {len(decisions)}")

    # 2. Build Decision Map (Prioritize Manual Decisions)
    # Map: TicketID -> NewCategory
    final_decisions = {}
    
    # 2a. Apply Manual Decisions First
    for d in decisions:
        final_decisions[d["id"]] = d["final_category"]

    # 3. Process Queue for Auto-Resolution
    auto_resolved_count = 0
    manual_review_needed = []

    for item in audit_queue:
        ticket_id = item["id"]
        
        # If already decided manually, skip logic
        if ticket_id in final_decisions:
            continue
            
        ai_conf = item["ai_confidence"]
        
        if ai_conf >= CONFIDENCE_THRESHOLD:
            # Rule 1: High Confidence Global
            final_decisions[ticket_id] = item["ai_label"]
            auto_resolved_count += 1
            
        elif item['human_label'] == "AJUDA E SUPORTE" and item['ai_label'] != "AJUDA E SUPORTE" and ai_conf > 0.70:
            # Rule 2: Laziness Override (Generic -> Specific)
            final_decisions[ticket_id] = item["ai_label"]
            auto_resolved_count += 1
            print(f"   [Override] ID {ticket_id}: AI '{item['ai_label']}' > Human 'AJUDA E SUPORTE' ({ai_conf:.2f})")

        # Phase 3 Rules: System Access Refinement
        elif "ACESSO A SISTEMAS" in item['human_label']:
             # Rule 3: Hierarchy Expansion (Human is substring of AI)
             # Ex: Human="OFFICE 365", AI="OFFICE 365 > EMAIL"
             if item['human_label'] in item['ai_label'] and len(item['ai_label']) > len(item['human_label']) and ai_conf > 0.75:
                 final_decisions[ticket_id] = item["ai_label"]
                 auto_resolved_count += 1
                 print(f"   [Hierarchy Chain] ID {ticket_id}: AI Expanded '{item['ai_label']}' ({ai_conf:.2f})")
            
             # Rule 4: NDD -> Printer Redirect
             # Ex: Human="NDD", AI="IMPRESSORA"
             elif "NDD" in item['human_label'] and "IMPRESSORA" in item['ai_label'] and ai_conf > 0.75:
                 final_decisions[ticket_id] = item["ai_label"]
                 auto_resolved_count += 1
                 print(f"   [NDD Fix] ID {ticket_id}: NDD -> Impressora ({ai_conf:.2f})")
             
             else:
                 manual_review_needed.append(item)

        else:
            # KEEP FOR MANUAL REVIEW
            manual_review_needed.append(item)

    # 4. Generate Clean Dataset
    clean_dataset = []
    changes_made = 0
    
    for ticket in dataset:
        ticket_id = ticket.get("id")
        
        if ticket_id in final_decisions:
            new_cat = final_decisions[ticket_id]
            if ticket["true_category"] != new_cat:
                ticket["true_category"] = new_cat
                changes_made += 1
        
        clean_dataset.append(ticket)

    # 5. Save Outputs
    
    # Save Clean Dataset
    with open(OUTPUT_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_dataset, f, indent=4, ensure_ascii=False)
        
    # Save Filtered Queue (overwrite original used by app? Or new file?)
    # Let's overwrite the main queue so the App sees the smaller list IMMEDIATELY.
    # But back up first.
    if os.path.exists(QUEUE_PATH):
        shutil.copy(QUEUE_PATH, QUEUE_PATH + ".bak")
        
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(manual_review_needed, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Resultados do Auto-Cleaning:")
    print(f"   - Decisões Manuais Aplicadas: {len(decisions)}")
    print(f"   - Auto-Resolvidos (Confiança > {CONFIDENCE_THRESHOLD}): {auto_resolved_count}")
    print(f"   - Enviados para Revisão Manual (App): {len(manual_review_needed)}")
    print(f"   -------------------------------------------------")
    print(f"   - Total de Tickets no Dataset Modificados: {changes_made}")
    print(f"   - Dataset Limpo Salvo em: {OUTPUT_DATASET_PATH}")
    print(f"   - Fila do App Atualizada: {len(audit_queue)} -> {len(manual_review_needed)} itens.")

if __name__ == "__main__":
    main()
