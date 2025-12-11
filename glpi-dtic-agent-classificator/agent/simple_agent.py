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
from glpi_agent.config import SANDBOX, ENVIRONMENT
from agent.llm_connector import LLMConnector

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
        self.client = GlpiClient(environment=ENVIRONMENT)
        self.client.init_session()
        
        if not self.client.session_token:
            logger.error("GLPI Authentication Failed! Check credentials.")
            sys.exit(1)
        
        logger.info("GLPI Connection Established.")

        # 2. Load Categories
        logger.info("Fetching Categories from GLPI API...")
        full_cat_map = self.client.categories_map()
        
        if not full_cat_map:
            logger.error("No categories found in GLPI. Exiting.")
            sys.exit(1)

        # 2.1 Load Context/Instructions (MOVED UP)
        self.context_map = {}
        try:
            context_path = os.path.join(os.path.dirname(__file__), "category_context.json")
            with open(context_path, "r", encoding="utf-8") as f:
                self.context_map = json.load(f)
            logger.info(f"Loaded context definitions for {len(self.context_map)} categories.")
        except FileNotFoundError:
            logger.warning(f"category_context.json not found at {context_path}. Using all categories (Fallback).")

        # 3. Filter Categories
        # Only keep categories that are present in the context_map
        if self.context_map:
            self.cat_map = {}
            # Logic: Iterating over CONTEXT allows us to simulate categories that don't exist in GLPI
            for name in self.context_map:
                if name in full_cat_map:
                    self.cat_map[name] = full_cat_map[name]
                elif SANDBOX:
                    # In Sandbox, we allow simulating categories that don't exist yet
                    # We assign ID 0 or -1 to indicate it's a simulated category
                    self.cat_map[name] = 0
            
            logger.info(f"Filtered Categories: {len(full_cat_map)} in GLPI / {len(self.context_map)} in Context -> {len(self.cat_map)} active for Simulation.")
        else:
            self.cat_map = full_cat_map
            logger.info("No context map found, using ALL fetched categories.")

        self.cat_names = list(self.cat_map.keys())
        self.cat_ids = list(self.cat_map.values())
        logger.info(f"Final Active Categories: {len(self.cat_names)}")

        # Context already loaded above
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
        
        # 5. Hybrid Intelligence
        try:
            self.llm = LLMConnector()
            self.use_llm = True
            logger.info("Hybrid Intelligence (LLM) Enabled.")
        except Exception as e:
            logger.error(f"Failed to init LLM: {e}. Falling back to standard vector search.")
            self.use_llm = False

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

    def predict_category(self, text: str) -> Tuple[str, int, float]:
        """
        Predicts the category for a given text using Hybrid logic.
        Returns: (category_name, category_id, confidence_score)
        """
        # 1. Understand
        query_embedding = self.model.encode(f"query: {text}", convert_to_tensor=True, device=DEVICE)
        
        # 2. Match - Get Top candidates
        scores = util.cos_sim(query_embedding, self.cat_embeddings)[0]
        
        # Standard Vector Best
        best_score_idx = torch.argmax(scores).item()
        best_score = scores[best_score_idx].item()
        vector_suggested_cat = self.cat_names[best_score_idx]
        vector_suggested_id = self.cat_ids[best_score_idx]
        
        # --- Hybrid Logic ---
        final_cat_name = vector_suggested_cat
        final_cat_id = vector_suggested_id
        final_conf = best_score
        
        if self.use_llm and best_score > 0.60:
            # Get Top 5
            top_k = min(5, len(self.cat_names))
            top_results = torch.topk(scores, k=top_k)
            
            top_indices = top_results.indices.tolist()
            top_names = [self.cat_names[i] for i in top_indices]
            
            logger.info(f"Vector Top 1: {vector_suggested_cat} ({best_score:.4f})")
            logger.info("Asking LLM Judge...")
            
            llm_decision = self.llm.decide_category(text, top_names)
            llm_cat = llm_decision.get("category")
            llm_reason = llm_decision.get("reason", "No reason provided")
            
            if llm_cat and llm_cat in self.cat_map:
                final_cat_name = llm_cat
                final_cat_id = self.cat_map[llm_cat]
                final_conf = 0.95 # Artificial high confidence for LLM choice
                logger.info(f"LLM Choice: \033[92m{final_cat_name}\033[0m")
                logger.info(f"Reason: {llm_reason}")
            else:
                logger.warning(f"LLM returned invalid category: {llm_cat}. Keeping vector choice.")
        
        return final_cat_name, final_cat_id, final_conf

    def handle_conversation(self, history: List[Dict]) -> str:
        """
        Delegates the conversation to the LLM.
        """
        if not self.use_llm:
            return "Erro: Módulo de IA indisponível."
            
        # Limit category list to top 100
        return self.llm.service_desk_dialog(history, self.cat_names[:100])
        
        text = join_title_description(title, content)
        
        logger.info(f"--- Processing Ticket #{tid} ---")
        logger.info(f"Title: {title}")
        
        # Call Predict
        final_cat_name, final_cat_id, final_conf = self.predict_category(text)
        
        # Get current category name for logging
        current_cat_name = "Uncategorized/Unknown"
        for name, cid in self.cat_map.items():
            if cid == current_cat_id:
                current_cat_name = name
                break
        
        logger.info(f"Current: {current_cat_name} | Suggested: {final_cat_name} | Conf: {final_conf:.4f}")

        # 3. Decision
        if final_conf < CONFIDENCE_THRESHOLD:
            logger.info("Action: SKIP (Low Confidence)")
            self.stats["skipped_low_conf"] += 1
            return

        if final_cat_id == current_cat_id and current_cat_id not in [0, None]:
            logger.info("Action: SKIP (Already Correct)")
            self.stats["skipped_correct"] += 1
            return

        # 4. Update
        logger.info(f"Action: UPDATE -> Changing to {final_cat_name}")
        
        if SANDBOX:
            logger.info("SANDBOX MODE: Skipping actual update.")
            self.stats["updated"] += 1 
            return

        try:
            success = self.client.update_ticket_category(tid, final_cat_id)
            
            if success:
                logger.info("GLPI Update: SUCCESS")
                self.stats["updated"] += 1
                msg = f"Agente Híbrido: Recategorizado automaticamente para '{final_cat_name}'."
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
            tickets = self.client.search_items("Ticket", {"is_deleted": "0", "status": "notold", "sort": "id", "order": "DESC"})
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
