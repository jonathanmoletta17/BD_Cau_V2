import unittest
from unittest.mock import AsyncMock, MagicMock
from src.services.chat_service import ChatService
from src.models import ChatMessage
from src.models.state import IntentType

class TestChatIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_llm = MagicMock()
        self.mock_llm.chat_completion = AsyncMock()
        self.mock_llm.extract_entities = AsyncMock()
        
        self.mock_classifier = MagicMock()
        self.mock_classifier.classify = AsyncMock()
        
        self.service = ChatService(self.mock_llm, self.mock_classifier)

    async def test_full_triage_flow_integration(self):
        # 1. User sends first message -> INTENT DETECTION
        self.mock_llm.chat_completion.return_value = "ACCESS"
        # Mock progressive extraction: 1. System, 2. Action, 3. Beneficiary
        self.mock_llm.extract_entities.side_effect = [
            {"system": "SOE"},
            {"action": "Liberar"},
            {"beneficiary_name": "João"}
        ]
        
        msg1 = [ChatMessage(role="user", content="Quero acesso ao SOE")]
        resp1 = await self.service.handle_message(msg1)
        
        # Expectation: State initialized to ACCESS, NLU called, Flow asks next question
        self.assertEqual(self.service.state.intent, IntentType.ACCESS)
        self.mock_llm.extract_entities.assert_called()
        self.assertIn("role", resp1)
        
        # 2. User answers Action -> NLU Extraction
        # Mock extract_entities to return the action
        self.mock_llm.extract_entities.return_value = {"action": "Liberar"}
        
        msg2 = [ChatMessage(role="user", content="Liberar")]
        resp2 = await self.service.handle_message(msg2)
        
        # Expectation: Action slot filled, Flow asks for Beneficiary
        self.assertEqual(self.service.state.slots["action"].value, "Liberar")
        
        # 3. User answers Beneficiary -> COMPLETION
        self.mock_llm.extract_entities.return_value = {"beneficiary_name": "João"}
        self.mock_classifier.classify.return_value = MagicMock(
            ticket_type=2,
            urgency=3,
            suggested_title="Ticket Title",
            selected_category_name="Category"
        )
        self.mock_classifier.classify.return_value.model_dump.return_value = {}
        
        msg3 = [ChatMessage(role="user", content="João")]
        resp3 = await self.service.handle_message(msg3)
        
        # Expectation: "classified" action, DONE
        self.assertEqual(resp3["action"], "classified")

if __name__ == '__main__':
    unittest.main()
