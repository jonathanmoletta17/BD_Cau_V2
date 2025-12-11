import sys
import os
import json
import logging

# Add project root to path
sys.path.append("/app")

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

try:
    from agent.simple_agent import SimpleAgent
    
    # Mocking init to avoid connection if possible? 
    # No, SimpleAgent logic is tightly coupled with GLPI connection.
    # We assume the container has valid env vars.
    
    def predict(title, description):
        try:
            agent = SimpleAgent()
            
            # Create a mock ticket dict
            # SimpleAgent.process_ticket expects a dict with 'name', 'content', 'id'
            ticket = {
                "id": 0, # Dummy ID
                "name": title,
                "content": description,
                "itilcategories_id": 0
            }
            
            # We want to capture the classification result specifically.
            # SimpleAgent process_ticket logs and updates GLPI. It doesn't return the category.
            # We need to hack/subclass it or modify it to return the value.
            # Since we can't easily modify the source code in the container permanently,
            # We will use a subclass here that overrides process_ticket to just return the prediction.
            
            return run_prediction_logic(agent, ticket)
            
        except Exception as e:
            return {"error": str(e)}

    def run_prediction_logic(agent, ticket):
        # Re-implementing the core logic from SimpleAgent.process_ticket
        # focused only on prediction
        
        from glpi_agent.preprocess import join_title_description
        from sentence_transformers import util
        import torch
        
        title = ticket.get("name", "")
        content = ticket.get("content", "")
        text = join_title_description(title, content)
        
        query_embedding = agent.model.encode(f"query: {text}", convert_to_tensor=True, device=agent.model.device)
        scores = util.cos_sim(query_embedding, agent.cat_embeddings)[0]
        
        best_score_idx = torch.argmax(scores).item()
        best_score = scores[best_score_idx].item()
        vector_suggested_cat = agent.cat_names[best_score_idx]
        vector_suggested_id = agent.cat_ids[best_score_idx]
        
        final_cat_name = vector_suggested_cat
        final_conf = best_score
        reason = "Vector Match"
        
        # Hybrid Logic (Simplified for verification)
        if agent.use_llm and best_score > 0.60:
            top_k = min(5, len(agent.cat_names))
            top_results = torch.topk(scores, k=top_k)
            top_names = [agent.cat_names[i] for i in top_results.indices.tolist()]
            
            try:
                llm_decision = agent.llm.decide_category(text, top_names)
                llm_cat = llm_decision.get("category")
                if llm_cat and llm_cat in agent.cat_map:
                    final_cat_name = llm_cat
                    final_conf = 0.95
                    reason = llm_decision.get("reason", "LLM Decision")
            except Exception as e:
                reason = f"LLM Error: {e}"

        return {
            "category": final_cat_name,
            "confidence": float(final_conf),
            "reason": reason,
            "text_processed": text
        }

    if __name__ == "__main__":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing arguments. Usage: python predict_wrapper.py title description"}))
            sys.exit(1)
            
        t = sys.argv[1]
        d = sys.argv[2]
        result = predict(t, d)
        print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": f"Import/Init failed: {str(e)}"}))
