import os
import sys
import json
import torch
from sentence_transformers import util

# Ensure we can import from agent/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agent.simple_agent import SimpleAgent

DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "datasets", "validation_dataset.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "audit_queue.json")

def main():
    print(">>> Initializing Audit Agent...")
    # Initialize agent to load model, categories, and contexts
    agent = SimpleAgent()
    
    print(f"\n>>> Loading dataset from {DATASET_PATH}...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    audit_queue = []
    
    print(f">>> Auditing {len(dataset)} tickets...")
    
    for item in dataset:
        ticket_id = item.get("id")
        text = item.get("text", "")
        true_category = item.get("true_category", "")
        
        # 1. Classify
        # We reuse the agent's model and embeddings directly for efficiency
        query_embedding = agent.model.encode(f"query: {text}", convert_to_tensor=True, device=agent.model.device)
        scores = util.cos_sim(query_embedding, agent.cat_embeddings)[0]
        best_score_idx = torch.argmax(scores).item()
        confidence = scores[best_score_idx].item()
        
        predicted_category = agent.cat_names[best_score_idx]
        
        # 2. Extract Reasoning (Context Definition)
        # Why did the AI choose this?
        reasoning = agent.context_map.get(predicted_category, "Sem definição de contexto.")
        
        # 3. Detect Discrepancy
        # We are looking for cases where AI disagrees with Human
        # OR where confidence is high but Human says something else
        
        if predicted_category != true_category:
            audit_item = {
                "id": ticket_id,
                "text": text,
                "human_label": true_category,
                "ai_label": predicted_category,
                "ai_confidence": round(confidence, 4),
                "ai_reasoning": reasoning,
                "status": "pending" # pending review
            }
            audit_queue.append(audit_item)
            
    print(f"\n>>> Audit Complete.")
    print(f"Total Tickets: {len(dataset)}")
    print(f"Discrepancies Found: {len(audit_queue)} ({len(audit_queue)/len(dataset)*100:.1f}%)")
    
    # Sort by confidence (highest confidence discrepancies first - most likely human errors)
    audit_queue.sort(key=lambda x: x["ai_confidence"], reverse=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_queue, f, indent=2, ensure_ascii=False)
        
    print(f">>> Audit queue saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
