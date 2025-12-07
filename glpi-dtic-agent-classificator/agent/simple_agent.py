import os
import sys
import time
import json
import logging
import torch
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration & Credentials ---
os.environ["AGENT_DEVICE"] = os.getenv("AGENT_DEVICE", "cuda")

from sentence_transformers import SentenceTransformer, util

# Ensure local imports work
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from glpi_agent.glpi_client import GlpiClient
from glpi_agent.preprocess import join_title_description
from glpi_agent.config import SANDBOX

# --- Constants ---
CONFIDENCE_THRESHOLD = 0.70
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SimpleAgent")

class SimpleAgent:
    def __init__(self):
        logger.info("Initializing Simple Agent...")
        
        # 1. Connect to GLPI
        self.client = GlpiClient(environment="test")
        self.client.init_session()
        
        if not self.client.session_token:
            logger.error("GLPI Authentication Failed! Check credentials.")
            sys.exit(1)
        
        logger.info("GLPI Connection Established.")

        # 2. Load Categories
        logger.info("Fetching Categories from GLPI API...")
        self.cat_map = self.client.categories_map()
        
        if not self.cat_map:
            logger.error("No categories found in GLPI. Exiting.")
            sys.exit(1)
            
        self.cat_names = list(self.cat_map.keys())
        self.cat_ids = list(self.cat_map.values())
        logger.info(f"Loaded {len(self.cat_names)} categories.")

        # 2.1 Load Context/Instructions
        self.context_map = {}
        try:
            context_path = os.path.join(os.path.dirname(__file__), "category_context.json")
            with open(context_path, "r", encoding="utf-8") as f:
                self.context_map = json.load(f)
            logger.info(f"Loaded context definitions for {len(self.context_map)} categories.")
        except FileNotFoundError:
            logger.warning(f"category_context.json not found at {context_path}. Using category names only.")

        # 3. Load Model
        logger.info(f"Loading Model on {DEVICE}...")
        self.model = SentenceTransformer("intfloat/multilingual-e5-large", device=DEVICE)
        
        logger.info("Encoding Category Knowledge Base...")
        
        # Combine Name + Context for richer embedding
        passages = []
        for name in self.cat_names:
            context = self.context_map.get(name, "")
            text_to_embed = f"{name}: {context}" if context else name
            passages.append(f"passage: {text_to_embed}")
            
        self.cat_embeddings = self.model.encode(
            passages, 
            convert_to_tensor=True, 
            device=DEVICE
        )
        
        # 4. Statistics
        self.stats = {
            "processed": 0,
            "updated": 0,
            "skipped_low_conf": 0,
            "skipped_correct": 0,
            "errors": 0
        }
        logger.info("Agent Ready.")

    def save_report(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        # Save reports to project_root/reports
        report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"report_{date_str}.json")
        
        report_data = {
            "date": date_str,
            "summary": self.stats,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def process_ticket(self, ticket: Dict):
        self.stats["processed"] += 1
        tid = ticket.get("id")

        title = ticket.get("name", "")
        content = ticket.get("content", "")
        current_cat_id = ticket.get("itilcategories_id")
        
        text = join_title_description(title, content)
        
        logger.info(f"--- Processing Ticket #{tid} ---")
        logger.info(f"Title: {title}")
        
        # 1. Understand
        query_embedding = self.model.encode(f"query: {text}", convert_to_tensor=True, device=DEVICE)
        
        # 2. Match
        scores = util.cos_sim(query_embedding, self.cat_embeddings)[0]
        best_score_idx = torch.argmax(scores).item()
        best_score = scores[best_score_idx].item()
        
        suggested_cat_name = self.cat_names[best_score_idx]
        suggested_cat_id = self.cat_ids[best_score_idx]
        
        # Get current category name for logging
        current_cat_name = "Uncategorized/Unknown"
        for name, cid in self.cat_map.items():
            if cid == current_cat_id:
                current_cat_name = name
                break
        
        logger.info(f"Current: {current_cat_name} | Suggested: {suggested_cat_name} | Conf: {best_score:.4f}")

        # 3. Decision
        if best_score < CONFIDENCE_THRESHOLD:
            logger.info("Action: SKIP (Low Confidence)")
            self.stats["skipped_low_conf"] += 1
            return

        if suggested_cat_id == current_cat_id:
            logger.info("Action: SKIP (Already Correct)")
            self.stats["skipped_correct"] += 1
            return

        # 4. Update
        logger.info(f"Action: UPDATE -> Changing to {suggested_cat_name}")
        
        if SANDBOX:
            logger.info("SANDBOX MODE: Skipping actual update.")
            self.stats["updated"] += 1 # Count as updated for stats in sandbox
            return

        try:
            success = self.client.update_ticket_category(tid, suggested_cat_id)
            
            if success:
                logger.info("GLPI Update: SUCCESS")
                self.stats["updated"] += 1
                msg = f"Agente AI: Recategorizado automaticamente de '{current_cat_name}' para '{suggested_cat_name}' (Confiança: {best_score:.2f})."
                self.client.add_followup(tid, msg)
            else:
                logger.error("GLPI Update: FAILED")
                self.stats["errors"] += 1
        except Exception as e:
            logger.error(f"Error updating ticket: {e}")
            self.stats["errors"] += 1

    def run_batch(self, limit=5):
        logger.info("Fetching recent tickets from GLPI...")
        try:
            tickets = self.client.search_items("Ticket", {"is_deleted": "0", "status": "notold"})
            if not tickets:
                logger.warning("No active tickets found.")
                return
        except Exception as e:
            logger.error(f"Failed to search tickets: {e}")
            return

        count = 0
        for t in tickets:
            if count >= limit: 
                break
            self.process_ticket(t)
            count += 1
        
        self.save_report()

if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run_batch(limit=5)
