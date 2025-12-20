import unittest
from src.models.state import SessionState, SlotDefinition, IntentType, TriageStep

class TestSessionState(unittest.TestCase):
    def setUp(self):
        # Initialize a typical state for "Access System"
        self.state = SessionState(
            intent=IntentType.ACCESS,
            step=TriageStep.COLLECTION
        )
        self.state.slots = {
            "system": SlotDefinition(name="system", description="System Name", question="Qual sistema?"),
            "action": SlotDefinition(name="action", description="Action", question="Qual ação?")
        }
        self.state.missing_fields = ["system", "action"]

    def test_initial_state(self):
        self.assertFalse(self.state.is_complete())
        self.assertEqual(len(self.state.missing_fields), 2)
        next_slot = self.state.get_next_missing_slot()
        self.assertIsNotNone(next_slot)
        # It should respect order in missing_fields
        self.assertEqual(next_slot.name, "system")

    def test_update_slot(self):
        # Update first slot
        self.state.update_slot("system", "SOE")
        
        self.assertEqual(self.state.slots["system"].value, "SOE")
        self.assertNotIn("system", self.state.missing_fields)
        self.assertIn("action", self.state.missing_fields)
        
        # Check next slot
        next_slot = self.state.get_next_missing_slot()
        self.assertEqual(next_slot.name, "action")

    def test_completion(self):
        self.state.update_slot("system", "SOE")
        self.state.update_slot("action", "Liberar")
        
        self.assertTrue(self.state.is_complete())
        self.assertIsNone(self.state.get_next_missing_slot())

if __name__ == '__main__':
    unittest.main()
