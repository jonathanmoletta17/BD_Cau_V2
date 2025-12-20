import json
import os
from typing import List, Dict, Optional
from src.services.llm_service import LLMService
from src.services.classifier_service import ClassifierService
from src.models import ClassificationRequest, ChatMessage
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "../config/prompts.json")

class ChatService:
    def __init__(self, llm_service: LLMService, classifier_service: ClassifierService):
        self.llm = llm_service
        self.classifier = classifier_service
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict:
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load prompts.json: {e}")
            return {}

    async def _check_viability(self, history: List[ChatMessage]) -> bool:
        """Determines if the conversation contains enough info for a ticket."""
        cfg = self.prompts.get("ticket_viability_check", {})
        system_prompt = cfg.get("system_prompt", "Return ONLY YES or NO.")
        
        # Build history text
        history_text = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in history[-5:]]) # Limit context
        user_prompt = cfg.get("user_template", "{history_text}").format(history_text=history_text)

        response = await self.llm.chat_completion(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            options={"temperature": 0.0}
        )
        
        clean_resp = response.strip().upper()
        logger.info(f"Viability Check: {clean_resp}")
        return "YES" in clean_resp

    async def handle_message(self, history: List[ChatMessage], session_id: str) -> Dict:
        """
        Simplified Handler:
        1. Check if user wants to quit.
        2. Check if we have enough info to open a ticket (Viability).
        3. If YES -> Classify and Propose.
        4. If NO -> Respond naturally to gather more info.
        """
        user_msg = history[-1].content
        
        # 1. Escape Hatch
        if user_msg.strip().lower() in ["cancelar", "sair", "parar", "resetar", "voltar"]:
            return {"role": "assistant", "content": "Entendido. Cancelei. Como posso ajudar com outra coisa?"}

        # 2. Viability Check (Can we create a ticket?)
        is_viable = await self._check_viability(history)
        
        if is_viable:
            # 3. Classify and Propose Ticket
            # Serialize history for the classifier to understand full context
            full_context = "\n".join([f"{m.role.upper()}: {m.content}" for m in history])
            
            logger.info("Request is viable. Calling Classifier.")
            try:
                classification = await self.classifier.classify(
                    ClassificationRequest(
                        title="Triage Request", 
                        description=full_context 
                    )
                )
                
                # Dynamic Response based on classification
                final_response = (
                    f"Entendido. Tenho informações suficientes.\n\n"
                    f"**Resumo do Chamado:**\n"
                    f"> **Assunto:** {classification.suggested_title}\n"
                    f"> **Categoria:** {classification.selected_category_name}\n"
                    f"> **Urgência:** {classification.urgency}/5\n\n"
                    f"Deseja confirmar a abertura deste chamado?"
                )
                
                return {
                    "role": "assistant",
                    "content": final_response,
                    "action": "classified",
                    "details": classification.model_dump()
                }
            except Exception as e:
                logger.error(f"Classifier error: {e}")
                print(f"DEBUG: Critical Classifier Error: {e}")
                import traceback
                traceback.print_exc()
                return {"role": "assistant", "content": "Tive um erro interno ao classificar. Pode tentar descrever novamente?"}
        
        else:
            # 4. Not Viable yet -> Conversational Follow-up
            # We treat the LLM as a helpful assistant that just wants to know more.
            # We inject a System Prompt to guide it towards IT support.
            
            system_role = (
                "Você é um Assistente de Suporte TI. O usuário tem um problema mas não deu detalhes suficientes para abrir um chamado. "
                "Faça UMA pergunta educada e específica para entender melhor o problema (ex: qual sistema, qual equipamento, mensagem de erro). "
                "Mantenha curto. Responda SEMPRE em Português."
            )
            
            # Pass recent history so it knows what was already said
            messages = [{"role": "system", "content": system_role}] + [m.model_dump() for m in history[-5:]]
            
            ai_response = await self.llm.chat_completion(messages)
            
            return {"role": "assistant", "content": ai_response}
