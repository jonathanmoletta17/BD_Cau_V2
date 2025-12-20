import unittest
from src.services.triage_flow import TriageFlow
from src.models.state import IntentType

class TestTriageFlow(unittest.TestCase):
    
    def test_flow_initialization_access(self):
        state = TriageFlow.initialize_state(IntentType.ACCESS)
        self.assertEqual(len(state.missing_fields), 3)
        self.assertEqual(state.missing_fields[0], "system")
        
    def test_next_question_logic(self):
        state = TriageFlow.initialize_state(IntentType.ACCESS)
        
        # 1. First question should be about System
        response = TriageFlow.get_next_response(state)
        self.assertIn("Para qual sistema", response)
        
        # 2. Fill System -> Next should be Action
        state.update_slot("system", "SOE")
        response = TriageFlow.get_next_response(state)
        self.assertIn("Qual ação", response)
        
        # 3. Fill Action -> Next should be Beneficiary
        state.update_slot("action", "Liberar")
        response = TriageFlow.get_next_response(state)
        self.assertIn("nome completo", response)
        
        # 4. Fill All -> Done
        state.update_slot("beneficiary_name", "João Silva")
        response = TriageFlow.get_next_response(state)
        self.assertEqual(response, "DONE")

if __name__ == '__main__':
    unittest.main()
