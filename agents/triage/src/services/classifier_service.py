import json
import os
from typing import List, Optional
from src.models import ClassificationRequest, ClassificationResponse, CategoryScore
from src.services.llm_service import LLMService
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

CATEGORIES_FILE = "categories_list.json"

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

    async def classify(self, request: ClassificationRequest) -> ClassificationResponse:
        # Reload cache if empty (lazy load)
        if not self.categories_cache:
            self._load_categories()

        if not self.categories_cache:
             raise ValueError("No categories available to classify against. Please run sync.")

        # --- Stage 1: Full Context Construction ---
        # Build the menu list
        # Format: "- <CompleteName> (ID: <ID>)"
        # We can optimize token usage by stripping common prefixes if needed, but for now full name is safer.
        
        cat_list_str = "\n".join([
            f"- {c['completename']} (ID: {c['id']})"
            for c in self.categories_cache
        ])

        # --- Stage 2: Prompting ---
        logger.info(f"Classifying ticket '{request.title}' using Full Context ({len(self.categories_cache)} categories)")
        
        system_prompt = (
            "You are an expert IT Helpdesk Dispatcher. Your goal is to select the BEST GLPI category for a user ticket.\n"
            "You will receive the ticket content and a COMPLETE list of available categories.\n"
            "Respond ONLY with a JSON object containing 'selected_category_id' (int) and 'reasoning' (string)."
        )

        user_prompt = f"""
INSTRUCTIONS:
1. **CRITICAL FALLBACK RULE**: 
   - If the request is about **Facilities** (Air Conditioner, Furniture, Plumbing, Power infra, Cleaning) or clearly **NON-IT** -> **MUST SELECT ID 5780 (Suporte Geral)**.
   - **DO NOT** classify Air Conditioners as "Falha Física" in Printers!
   - **DO NOT** classify Furniture as Hardware!

2. Analyze the ticket content carefully.
3. Determine **Ticket Type** (1=Incident, 2=Request).
4. Determine **Urgency** (1-5) and **Impact** (1-5).
5. Select the MOST SPECIFIC Category (if IT-related).

6. **Generate Detailed Reasoning**: Write a concise but professional explanation (in Portuguese) justifying your decisions. 
   - Structure: "Analysis: [User intent]. Metadata: [Why Urgency X/Impact Y]. Category: [Why this category]."
   - Example: "O usuário relatou lentidão no servidor. Classificado como Urgência Alta (4) pois afeta o setor financeiro (Impacto 3). Categorizado em Servidores pois trata-se de infraestrutura central."

6. **HINTS**:
   - "Monitor", "Teclado", "Mouse" -> **Periféricos**.
   - "Computador", "PC", "Não liga" -> **Desktops**.
   - "Adobe", "AutoCAD" -> **Softwares > Instalação**.

7. **Generate Standardized Title**: Create a concise, objective title (**STRICTLY IN PORTUGUESE**) following the pattern: "[Category] Short Description".
   - **[Category]**: Use ONLY the name of the **final sub-category** (Leaf Node). DO NOT use the full path.
     - WRONG: "[Hardware > Impressoras > Falha]"
     - RIGHT: "[Falha Física]" or "[Impressoras]"
   - **Short Description**: If the user input is vague (e.g., "Dúvida"), infer the likely topic.
     - User: "Assinatura" -> Title: "[Outlook] Configuração de Assinatura"
   - Examples (Portuguese Only):
     - User: "My printer is not working" -> Title: "[Impressoras] Falha no Equipamento"
     - User: "Server on fire" -> Title: "[Servidor] Falha Crítica de Hardware"
     - User: "Ar condicionado pingando" -> Title: "[Suporte Geral] Solicitação de Facilities"

TICKET:
Title: {request.title}
Description: {request.description}

AVAILABLE CATEGORIES:
{cat_list_str}

Respond with valid JSON only:
{{
    "selected_category_id": <int>,
    "ticket_type": <int>,
    "urgency": <int>,
    "impact": <int>,
    "suggested_title": "<string>",
    "reasoning": "<MarkDown text with the detailed analysis>"
}}
"""

        # --- Stage 3: LLM Inference ---
        llm_response_str = await self.llm.generate_response(user_prompt, system_prompt)
        
        # --- Stage 4: Parsing ---
        # Clean markdown code blocks if present
        cleaned_response = llm_response_str.strip()
        if cleaned_response.startswith("```"):
            # Remove first line (```json) and last line (```)
            lines = cleaned_response.splitlines()
            if len(lines) >= 2:
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_response = "\n".join(lines).strip()
        
        try:
            llm_data = json.loads(cleaned_response)
            selected_id = llm_data.get("selected_category_id")
            reasoning = llm_data.get("reasoning", "No reasoning provided")
            ticket_type = llm_data.get("ticket_type", 1)
            urgency = llm_data.get("urgency", 3)
            impact = llm_data.get("impact", 3)
            suggested_title = llm_data.get("suggested_title", request.title)
            
            # Find name
            selected_cat = next((c for c in self.categories_cache if c['id'] == selected_id), None)
            selected_name = selected_cat['completename'] if selected_cat else "Unknown"
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {llm_response_str}")
            # Fallback (maybe first item? or error)
            # For now, let's return a generic error or null
            return ClassificationResponse(
                selected_category_id=-1,
                selected_category_name="Unclassified (Parse Error)",
                confidence=0.0,
                reasoning=f"Failed to parse JSON. Raw: {llm_response_str}",
                ticket_type=1,
                urgency=3,
                impact=3,
                candidates=[]
            )

        # We don't have "candidates" in the same sense (scores), strictly speaking.
        # But we can return the chosen one as the single candidate.
        chosen_candidate = [CategoryScore(
            category_id=selected_id, 
            name=selected_name, 
            score=1.0, 
            description=""
        )]

        return ClassificationResponse(
            selected_category_id=selected_id,
            selected_category_name=selected_name,
            confidence=0.95, # High confidence if LLM picked it from full list
            reasoning=reasoning,
            ticket_type=ticket_type,
            urgency=urgency,
            impact=impact,
            suggested_title=suggested_title,
            candidates=chosen_candidate
        )
