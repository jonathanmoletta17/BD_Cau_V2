import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List

# Ensure local imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.simple_agent import SimpleAgent, DEVICE
from glpi_agent.config import SANDBOX

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("full_run.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("FullRun")

class FullRunAgent(SimpleAgent):
    def __init__(self):
        super().__init__()
        self.detailed_metrics = []

    def process_ticket_with_metrics(self, ticket: Dict):
        start_time = time.time()
        
        tid = ticket.get("id")
        title = ticket.get("name", "")
        content = ticket.get("content", "")
        current_cat_id = ticket.get("itilcategories_id")
        
        # Get current category name
        current_cat_name = "Uncategorized/Unknown"
        for name, cid in self.cat_map.items():
            if cid == current_cat_id:
                current_cat_name = name
                break

        # Run prediction logic (reusing parts of process_ticket but capturing data)
        from glpi_agent.preprocess import join_title_description
        from sentence_transformers import util
        import torch

        text = join_title_description(title, content)
        query_embedding = self.model.encode(f"query: {text}", convert_to_tensor=True, device=DEVICE)
        scores = util.cos_sim(query_embedding, self.cat_embeddings)[0]
        best_score_idx = torch.argmax(scores).item()
        best_score = scores[best_score_idx].item()
        
        suggested_cat_name = self.cat_names[best_score_idx]
        suggested_cat_id = self.cat_ids[best_score_idx]
        
        duration = time.time() - start_time
        
        # Determine Action
        action = "SKIP"
        if best_score < 0.80: # CONFIDENCE_THRESHOLD
            action = "SKIP_LOW_CONF"
        elif suggested_cat_id == current_cat_id:
            action = "SKIP_ALREADY_CORRECT"
        else:
            action = "UPDATE"
            # Call parent process_ticket to actually perform the update (or sandbox log)
            # But since we want to be careful and we are in a subclass, let's just call the logic directly if we wanted to update
            # For now, let's just use the parent's process_ticket to handle the side effects (logging, updating)
            # But process_ticket doesn't return info. 
            # So we will just record what WOULD happen here for the metrics.
            
            # Actually, to be safe and consistent, let's call the parent process_ticket 
            # so it does the actual work (including sandbox check)
            super().process_ticket(ticket)

        metric = {
            "ticket_id": tid,
            "title": title,
            "current_category": current_cat_name,
            "predicted_category": suggested_cat_name,
            "confidence": best_score,
            "action": action,
            "processing_time": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.detailed_metrics.append(metric)

    def run_full_scan(self, batch_size=50):
        logger.info("Starting Full Categorization Run...")
        logger.info(f"Sandbox Mode: {SANDBOX}")
        
        offset = 0
        total_processed = 0
        
        while True:
            logger.info(f"Fetching tickets offset {offset}...")
            # Use search_items with range if supported, or just fetch all and paginate manually if API doesn't support offset well
            # glpi_client.py has list_items_range(itemtype, start, end)
            
            try:
                tickets = self.client.list_items_range("Ticket", offset, offset + batch_size)
            except Exception as e:
                logger.error(f"Error fetching tickets: {e}")
                break
                
            if not tickets:
                logger.info("No more tickets found.")
                break
                
            for ticket in tickets:
                # Filter for not deleted if not already done by API
                if ticket.get("is_deleted") == 1:
                    continue
                    
                self.process_ticket_with_metrics(ticket)
                total_processed += 1
            
            if len(tickets) < batch_size:
                break
                
            offset += batch_size
            
        self.save_detailed_report()

    def save_detailed_report(self):
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"full_run_metrics_{date_str}.json")
        
        report_data = {
            "date": date_str,
            "total_processed": len(self.detailed_metrics),
            "sandbox": SANDBOX,
            "metrics": self.detailed_metrics
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed report saved to {report_path}")

if __name__ == "__main__":
    agent = FullRunAgent()
    agent.run_full_scan()
