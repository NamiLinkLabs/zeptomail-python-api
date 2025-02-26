import unittest
from unittest.mock import patch, MagicMock
from zeptomail import ZeptoMail

class TestZeptoMail(unittest.TestCase):
    def setUp(self):
        self.client = ZeptoMail("test-api-key")
    
    def test_build_email_address(self):
        # Test with name
        result = self.client._build_email_address("test@example.com", "Test User")
        self.assertEqual(result, {"address": "test@example.com", "name": "Test User"})
        
        # Test without name
        result = self.client._build_email_address("test@example.com")
        self.assertEqual(result, {"address": "test@example.com"})
    
    def test_build_recipient(self):
        result = self.client._build_recipient("test@example.com", "Test User")
        self.assertEqual(
            result, 
            {"email_address": {"address": "test@example.com", "name": "Test User"}}
        )
    
    @patch('requests.post')
    def test_send_email(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"message_id": "test-id"}}
        mock_post.return_value = mock_response
        
        # Call the method
        response = self.client.send_email(
            from_address="sender@example.com",
            from_name="Sender",
            to=[self.client.add_recipient("recipient@example.com", "Recipient")],
            subject="Test Email",
            html_body="<p>Test</p>"
        )
        
        # Assert the response
        self.assertEqual(response, {"data": {"message_id": "test-id"}})
        
        # Assert the request was made correctly
        mock_post.assert_called_once()
        
if __name__ == '__main__':
    unittest.main()
