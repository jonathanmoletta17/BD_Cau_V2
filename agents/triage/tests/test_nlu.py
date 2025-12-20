import unittest
from unittest.mock import AsyncMock, MagicMock
from src.services.llm_service import LLMService

class TestNLU(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.llm_service = LLMService(model="mock-model")
        # Mock the generate_response method to avoid real API calls during tests
        self.llm_service.generate_response = AsyncMock()

    async def test_extraction_success(self):
        # Mocking a successful JSON response
        self.llm_service.generate_response.return_value = '{"system": "SOE", "action": "liberar", "beneficiary_name": "João", "beneficiary_id": null}'
        
        input_text = "Preciso liberar acesso ao SOE para o João"
        schema = {"system": "str", "action": "str", "beneficiary_name": "str", "beneficiary_id": "str"}
        
        result = await self.llm_service.extract_entities(input_text, schema)
        
        self.assertEqual(result["system"], "SOE")
        self.assertEqual(result["action"], "liberar")
        self.assertEqual(result["beneficiary_name"], "João")
        self.assertIsNone(result["beneficiary_id"])

    async def test_extraction_json_cleanup(self):
        # Mocking a response with Markdown code blocks
        self.llm_service.generate_response.return_value = '```json\n{"system": "PROA"}\n```'
        
        input_text = "Acesso ao PROA"
        schema = {"system": "str"}
        
        result = await self.llm_service.extract_entities(input_text, schema)
        self.assertEqual(result["system"], "PROA")

    async def test_extraction_failure(self):
        # Mocking invalid JSON
        self.llm_service.generate_response.return_value = 'Not a JSON'
        
        result = await self.llm_service.extract_entities("test", {})
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
