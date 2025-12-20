import json
import os
from typing import List, Optional, Dict
from src.models import ClassificationRequest, ClassificationResponse, CategoryScore
from src.services.llm_service import LLMService
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


# Fix path to be relative to this file, not CWD
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATEGORIES_FILE = os.path.join(BASE_DIR, "categories_list.json")


class ClassifierService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.categories_cache = []
        self._load_categories()

    def _load_categories(self):
        if os.path.exists(CATEGORIES_FILE):
            try:
                with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                    self.categories_cache = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load categories for classifier: {e}")
        else:
            logger.warning("Categories file not found. Classifier might need a sync first.")

    def _get_root_categories(self) -> List[Dict]:
        return [c for c in self.categories_cache if c.get('level') == 1]

    def _get_children_categories(self, root_name: str) -> List[Dict]:
        # Filter strictly descendants
        prefix = f"{root_name} >"
        return [
            c for c in self.categories_cache 
            if c.get('completename', '').startswith(prefix)
        ]

    async def classify(self, request: ClassificationRequest) -> ClassificationResponse:
        # Reload cache if empty
        if not self.categories_cache:
            self._load_categories()
        print(f"DEBUG: Running Two-Step Classify. Cache size: {len(self.categories_cache)}")
        if not self.categories_cache:
             raise ValueError("No categories available to classify against. Please run sync.")

        # --- STEP 1: ROOT CLASSIFICATION ---
        roots = self._get_root_categories()
        root_str = "\n".join([f"- {c['name']} (ID: {c['id']})" for c in roots])
        
        logger.info(f"Step 1: Classifying Root for '{request.title}' against {len(roots)} roots.")

        system_prompt_root = (
            "You are a Triage Dispatcher. Select the broad Domain (Root Category) for this request.\n"
            "Respond ONLY with JSON: {'root_id': <int>, 'reasoning': <string>}"
        )
        user_prompt_root = f"""
TICKET: {request.description}

DOMAINS:
{root_str}


Select the most matching Domain ID.
CRITICAL: Output ONLY the JSON object. Do not add any introductory text.
"""
        root_response = await self.llm.generate_response(user_prompt_root, system_prompt_root)
        root_data = self._parse_json_response(root_response)
        
        if not root_data or 'root_id' not in root_data:
            logger.error(f"Failed Step 1. Raw: {root_response}")
            return self._create_error_response("Failed to identify ticket domain.")
            
        root_id = root_data['root_id']
        selected_root = next((r for r in roots if r['id'] == root_id), None)
        
        if not selected_root:
            logger.error(f"Invalid Root ID selected: {root_id}")
            return self._create_error_response("Selected domain is invalid.")

        # --- STEP 2: LEAF CLASSIFICATION ---
        children = self._get_children_categories(selected_root['completename'])
        
        # Fallback: If no children, simpler classification (or just return root)
        # But most roots in GLPI should have children. If empty, using Root as final.
        target_list = children if children else [selected_root]
        
        logger.info(f"Step 2: Classifying Leaf in '{selected_root['name']}' ({len(target_list)} candidates).")
        
        cat_str = "\n".join([f"- {c['completename']} (ID: {c['id']})" for c in target_list])
        
        system_prompt_leaf = (
            "You are an expert IT Helpdesk Dispatcher. Select the Final Category within the Service Domain.\n"
            "Respond ONLY with standard JSON structure."
        )
        
        user_prompt_leaf = f"""
INSTRUCTIONS:
1. Analyze the ticket content.
2. Select the BEST category from the list below (Domain: {selected_root['name']}).
3. Determine Urgency/Impact (1-5).
4. Generate 'suggested_title': "[SubCategory] User Intent" (Portuguese).

TICKET DESCRIPTION:
{request.description}

AVAILABLE CATEGORIES ({selected_root['name']}):
{cat_str}

JSON FORMAT:
{{
    "selected_category_id": <int>,
    "ticket_type": <int (1=Inc, 2=Req)>,
    "urgency": <int>,
    "impact": <int>,
    "suggested_title": "<string>",
    "reasoning": "<string>"
}}
"""
        leaf_response = await self.llm.generate_response(user_prompt_leaf, system_prompt_leaf)
        leaf_data = self._parse_json_response(leaf_response)
        
        if not leaf_data:
             # Fallback to Root if Leaf fails? Or Error?
             # Let's fallback to Root to be safe, but mark low confidence.
             logger.warning("Step 2 Failed. Falling back to Root.")
             return ClassificationResponse(
                selected_category_id=selected_root['id'],
                selected_category_name=selected_root['completename'],
                confidence=0.5,
                reasoning=f"Step 2 failed. Domain identified: {root_data.get('reasoning')}",
                ticket_type=1,
                urgency=3,
                impact=3,
                suggested_title=f"[{selected_root['name']}] Nova Solicitação",
                candidates=[]
             )

        # Success Step 2
        selected_id = leaf_data.get("selected_category_id")
        selected_leaf = next((c for c in target_list if c['id'] == selected_id), None)
        selected_name = selected_leaf['completename'] if selected_leaf else "Unknown"

        return ClassificationResponse(
            selected_category_id=selected_id,
            selected_category_name=selected_name,
            confidence=0.95,
            reasoning=leaf_data.get("reasoning", ""),
            ticket_type=leaf_data.get("ticket_type", 1),
            urgency=leaf_data.get("urgency", 3),
            impact=leaf_data.get("impact", 3),
            suggested_title=leaf_data.get("suggested_title", request.title),
            candidates=[CategoryScore(category_id=selected_id, name=selected_name, score=1.0, description="")]
        )

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        clean = text.strip()
        
        # Try finding the first '{' and last '}'
        start = clean.find('{')
        end = clean.rfind('}')
        
        if start != -1 and end != -1:
             clean = clean[start:end+1]
        
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            logger.error(f"JSON Parse Error. Raw text: {text}")
            return None

    def _create_error_response(self, reasoning: str) -> ClassificationResponse:
        return ClassificationResponse(
            selected_category_id=-1,
            selected_category_name="Unclassified",
            confidence=0.0,
            reasoning=reasoning,
            ticket_type=1,
            urgency=3,
            impact=3,
            candidates=[]
        )
