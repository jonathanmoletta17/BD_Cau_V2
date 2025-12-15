import json
from typing import List, Dict
from src.services.llm_service import LLMService
from src.services.classifier_service import ClassifierService
from src.models import ClassificationRequest, ChatMessage
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class ChatService:
    def __init__(self, llm_service: LLMService, classifier_service: ClassifierService):
        self.llm = llm_service
        self.classifier = classifier_service
        
        self.system_prompt = """
        You are a helpful IT Support Assistant for a GLPI Helpdesk.
        Your goal is to capture the user's request and Open a Ticket.

        BEHAVIOR:
        1. If the user says "Hello", greet them and ask how to help.
        2. If the user describes a problem OR a specific request (e.g. "Install Adobe", "Need a headset", "Printer broken"), acknowledge it briefy and IMMEDIATELY output the CLASSIFY token.
        3. Only ask for clarification if the request is completely meaningless (e.g. "It fails").
        
        TOKEN FORMAT:
        [[CLASSIFY: <concise summary of the request>]]
        
        Example:
        User: "I need a mouse."
        Assistant: "Understood, I'll register that request. [[CLASSIFY: Request for a new mouse]]"
        """

    async def handle_message(self, history: List[ChatMessage]) -> Dict:
        """
        Process incoming chat history.
        """
        # Convert Pydantic models to dicts for LLM Service
        messages = [{"role": m.role, "content": m.content} for m in history]
        
        # Prepend system prompt
        full_history = [{"role": "system", "content": self.system_prompt}] + messages
        
        # 1. Get LLM Response
        ai_text = await self.llm.chat_completion(full_history)
        
        # 2. Check for Intent (Naive implementation for MVP)
        # In a real agent, we would use Function Calling / Tool Use API
        if "[[CLASSIFY:" in ai_text:
            # Extract description
            start = ai_text.find("[[CLASSIFY:") + len("[[CLASSIFY:")
            end = ai_text.find("]]", start)
            issue_description = ai_text[start:end].strip()
            
            # Remove the token from the visible response
            clean_response = ai_text.replace(f"[[CLASSIFY: {issue_description}]]", "").strip()
            
            # 3. Call Classifier
            logger.info(f"Intent detected: Classifying description='{issue_description}'")
            try:
                # Use description as title (truncated) if explicit title not available
                classification = await self.classifier.classify(
                    ClassificationRequest(
                        title=issue_description[:50], 
                        description=issue_description
                    )
                )
                
                # Format Type/Urgency for display
                type_str = "Request" if classification.ticket_type == 2 else "Incident"
                urg_str = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Very Low"}.get(classification.urgency, "Medium")
                
                # Append classification info to response
                clean_response += f"\n\n(System Note: **{classification.suggested_title}** | Category: **{classification.selected_category_name}** | Type: {type_str} | Urgency: {urg_str})"
                
                return {
                    "role": "assistant",
                    "content": clean_response,
                    "action": "classified",
                    "details": classification.model_dump()
                }
            except Exception as e:
                logger.error(f"Classification failed during chat: {e}")
                clean_response += "\n(I tried to categorize your request but encountered an error. Please try again.)"
                return {"role": "assistant", "content": clean_response}

        return {
            "role": "assistant",
            "content": ai_text
        }
