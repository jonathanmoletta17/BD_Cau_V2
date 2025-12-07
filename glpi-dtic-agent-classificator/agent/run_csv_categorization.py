import os
import sys
import json
import time
import csv
import logging
from datetime import datetime
from typing import Dict, List, Set

# Ensure local imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.simple_agent import SimpleAgent, DEVICE
from glpi_agent.config import SANDBOX, CSV_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("csv_categorization.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CSVCategorization")

class CSVCategorizer(SimpleAgent):
    def __init__(self, csv_path: str):
        super().__init__()
        self.csv_path = csv_path
        self.target_ids = self._load_csv_ids()
        self.detailed_metrics = []
        self.processed_count = 0
        self.skipped_count = 0

    def _load_csv_ids(self) -> Set[int]:
        """Load ticket IDs from CSV file"""
        ids = set()
        logger.info(f"Loading ticket IDs from {self.csv_path}...")
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            header = lines[0].strip().split(';')
            
            # Find ID column
            id_col_idx = None
            for i, h in enumerate(header):
                if 'ID' in h.upper():
                    id_col_idx = i
                    break
            
            if id_col_idx is None:
                raise ValueError("Could not find ID column in CSV!")
            
            # Parse IDs
            for line in lines[1:]:
                parts = line.strip().split(';')
                if len(parts) > id_col_idx:
                    ticket_id_str = parts[id_col_idx].strip().replace('"', '').replace(' ', '')
                    if ticket_id_str and ticket_id_str.isdigit():
                        ids.add(int(ticket_id_str))
        
        logger.info(f"Loaded {len(ids)} ticket IDs from CSV")
        return ids

    def process_ticket_with_metrics(self, ticket: Dict):
        """Process a single ticket and record metrics"""
        start_time = time.time()
        
        tid = ticket.get("id")
        
        # Skip if not in CSV
        if tid not in self.target_ids:
            self.skipped_count += 1
            return
        
        title = ticket.get("name", "")
        content = ticket.get("content", "")
        current_cat_id = ticket.get("itilcategories_id")
        
        # Get current category name
        current_cat_name = "Uncategorized/Unknown"
        for name, cid in self.cat_map.items():
            if cid == current_cat_id:
                current_cat_name = name
                break

        # Run prediction
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
        if best_score < 0.80:
            action = "SKIP_LOW_CONF"
        elif suggested_cat_id == current_cat_id:
            action = "SKIP_ALREADY_CORRECT"
        else:
            action = "UPDATE"
            # Call parent to handle actual update
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
        self.processed_count += 1
        
        # Log progress every 100 tickets
        if self.processed_count % 100 == 0:
            logger.info(f"Progress: {self.processed_count}/{len(self.target_ids)} tickets processed")

    def run_csv_categorization(self, batch_size=50):
        logger.info("=" * 80)
        logger.info("Starting CSV-Based Categorization")
        logger.info("=" * 80)
        logger.info(f"Target tickets from CSV: {len(self.target_ids)}")
        logger.info(f"Sandbox Mode: {SANDBOX}")
        logger.info(f"Environment: {self.client.env}")
        
        if not SANDBOX:
            logger.warning("⚠️  SANDBOX IS DISABLED - CHANGES WILL BE APPLIED TO DATABASE!")
            time.sleep(2)  # Give time to cancel if needed
        
        offset = 0
        
        while self.processed_count < len(self.target_ids):
            logger.info(f"Fetching batch at offset {offset}...")
            
            try:
                tickets = self.client.list_items_range("Ticket", offset, offset + batch_size)
            except Exception as e:
                logger.error(f"Error fetching tickets: {e}")
                break
                
            if not tickets:
                logger.info("No more tickets from API")
                break
                
            for ticket in tickets:
                if ticket.get("is_deleted") == 1:
                    continue
                    
                self.process_ticket_with_metrics(ticket)
            
            if len(tickets) < batch_size:
                break
                
            offset += batch_size
            
        self.save_detailed_report()
        self.print_summary()

    def save_detailed_report(self):
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"csv_categorization_{date_str}.json")
        
        report_data = {
            "date": date_str,
            "total_target": len(self.target_ids),
            "total_processed": self.processed_count,
            "total_skipped": self.skipped_count,
            "sandbox": SANDBOX,
            "metrics": self.detailed_metrics
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed report saved to {report_path}")

    def print_summary(self):
        logger.info("=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Target tickets (from CSV): {len(self.target_ids)}")
        logger.info(f"Tickets processed: {self.processed_count}")
        logger.info(f"Tickets skipped: {self.skipped_count}")
        
        actions = {}
        for m in self.detailed_metrics:
            action = m['action']
            actions[action] = actions.get(action, 0) + 1
        
        logger.info("\nActions breakdown:")
        for action, count in actions.items():
            pct = (count / len(self.detailed_metrics) * 100) if self.detailed_metrics else 0
            logger.info(f"  {action}: {count} ({pct:.2f}%)")
        
        logger.info("=" * 80)

if __name__ == "__main__":
    csv_file = CSV_PATH
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        sys.exit(1)
    
    agent = CSVCategorizer(csv_file)
    agent.run_csv_categorization()
