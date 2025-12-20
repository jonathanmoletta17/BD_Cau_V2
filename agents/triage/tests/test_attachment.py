
import unittest
from unittest.mock import MagicMock, patch, AsyncMock, mock_open
import json
import os
from src.services.glpi_client import GLPIClient

class TestGLPIAttachment(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = GLPIClient()
        self.client.client.post = AsyncMock()
        
        # Mock Session
        self.client.session_token = "mock_session_token"
        self.client.write_url = "http://mock-glpi/api"
        self.client.write_app_token = "mock_app_token"

    @patch("builtins.open", new_callable=mock_open, read_data=b"test_content")
    @patch("os.path.exists", return_value=True)
    async def test_upload_document_success(self, mock_exists, mock_file):
        # Setup Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 555, "message": "Document Added"}
        self.client.client.post.return_value = mock_response

        # Execute
        result = await self.client.upload_document(
            ticket_id=123,
            file_path="/tmp/test.png",
            filename="test.png",
            mime_type="image/png"
        )

        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 555)

        # Check API Call
        args, kwargs = self.client.client.post.call_args
        self.assertEqual(args[0], "http://mock-glpi/api/Document")
        
        # Check Headers
        headers = kwargs["headers"]
        self.assertEqual(headers["Session-Token"], "mock_session_token")
        
        # Check Data (Manifest)
        data = kwargs["data"]
        manifest = json.loads(data["uploadManifest"])
        self.assertEqual(manifest["input"]["items_id"], 123)
        self.assertEqual(manifest["input"]["_filename"], ["test.png"])
        
        # Check Files
        files = kwargs["files"]
        self.assertIn("filename[0]", files)

    @patch("os.path.exists", return_value=False)
    async def test_upload_document_file_not_found(self, mock_exists):
        result = await self.client.upload_document(123, "/invalid/path.png", "path.png")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
