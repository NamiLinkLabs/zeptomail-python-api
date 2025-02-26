import unittest
import json
from unittest.mock import patch, MagicMock
from zeptomail import ZeptoMail, ZeptoMailError

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
            from_address="test@example.com",
            from_name="Sender",
            to=[self.client.add_recipient("recipient@example.com", "Recipient")],
            subject="Test Email",
            html_body="<p>Test</p>"
        )
        
        # Assert the response
        self.assertEqual(response, {"data": {"message_id": "test-id"}})
        
        # Assert the request was made correctly
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_handle_success_response(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "message_id": "test-id",
                "code": "success",
                "additional_info": {"key": "value"},
                "message": "Email sent successfully"
            },
            "message": "success",
            "request_id": "req-123456",
            "object": "email"
        }
        mock_post.return_value = mock_response
        
        # Call the method
        response = self.client.send_email(
            from_address="test@example.com",
            from_name="Sender",
            to=[self.client.add_recipient("recipient@example.com", "Recipient")],
            subject="Test Email",
            html_body="<p>Test</p>"
        )
        
        # Assert the response is returned correctly
        self.assertEqual(response["data"]["message_id"], "test-id")
        self.assertEqual(response["data"]["code"], "success")
        self.assertEqual(response["request_id"], "req-123456")
    
    @patch('requests.post')
    def test_handle_error_response(self, mock_post):
        # Setup mock response with error
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {
                "code": "invalid_parameter",
                "message": "Invalid parameter provided",
                "details": [
                    {
                        "code": "missing_field",
                        "message": "This field is required",
                        "target": "to"
                    }
                ]
            },
            "request_id": "req-error-123"
        }
        mock_post.return_value = mock_response
        
        # Call the method and expect an exception
        with self.assertRaises(ZeptoMailError) as context:
            self.client.send_email(
                from_address="test@example.com",
                subject="Test Email",
                html_body="<p>Test</p>"
            )
        
        # Check the exception message
        self.assertIn("ZeptoMail API Error", str(context.exception))
        self.assertIn("Invalid parameter provided", str(context.exception))
        self.assertIn("to: This field is required", str(context.exception))
        
    @patch('requests.post')
    def test_specific_error_codes(self, mock_post):
        # Test TM_3201 GE_102 error (missing subject)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {
                "code": "TM_3201",
                "sub_code": "GE_102",
                "message": "Mandatory Field 'subject' was set as Empty Value.",
                "details": [
                    {
                        "target": "subject",
                        "message": "This field is required"
                    }
                ]
            },
            "request_id": "req-error-456"
        }
        mock_post.return_value = mock_response
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.send_email(
                from_address="test@example.com",
                to=[self.client.add_recipient("recipient@example.com")],
                subject="",
                html_body="<p>Test</p>"
            )
        
        # Check that the exception includes the solution
        self.assertIn("Set a non-empty subject", str(context.exception))
        
    def test_zeptomail_error_detail_messages(self):
        # Test with target and message
        error = ZeptoMailError(
            message="Test error",
            code="TEST_001",
            details=[
                {"target": "field1", "message": "Error in field1"},
                {"target": "field2", "message": "Error in field2"}
            ],
            request_id="test-req-123"
        )
        error_str = str(error)
        self.assertIn("field1: Error in field1", error_str)
        self.assertIn("field2: Error in field2", error_str)
        
        # Test with only message, no target
        error = ZeptoMailError(
            message="Test error",
            code="TEST_002",
            details=[
                {"message": "General error message"}
            ],
            request_id="test-req-456"
        )
        error_str = str(error)
        self.assertIn("General error message", error_str)
        
        # Test with empty details list
        error = ZeptoMailError(
            message="Test error",
            code="TEST_003",
            details=[],
            request_id="test-req-789"
        )
        error_str = str(error)
        self.assertNotIn("Details:", error_str)
        
    def test_get_error_solution(self):
        # Create a client instance for testing
        client = ZeptoMail("test-api-key")
        
        # Test with string solution
        solution = client._get_error_solution(
            "TM_3301", "SM_101", []
        )
        self.assertEqual(solution, "Check your API request syntax for valid JSON format.")
        
        # Test with dictionary solution and matching target
        solution = client._get_error_solution(
            "TM_3201", "GE_102", [{"target": "subject", "message": "This field is required"}]
        )
        self.assertEqual(solution, "Set a non-empty subject for your email.")
        
        # Test with dictionary solution but no matching target
        # Should return the first solution in the dictionary
        solution = client._get_error_solution(
            "TM_3201", "GE_102", [{"target": "unknown_field", "message": "Error"}]
        )
        self.assertIsNotNone(solution)  # Should return some solution (first in dict)
        
        # Test with no matching error code
        solution = client._get_error_solution(
            "UNKNOWN_CODE", "UNKNOWN_SUB", []
        )
        self.assertIsNone(solution)
        
    @patch('requests.post')
    def test_invalid_json_response(self, mock_post):
        # Setup mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        # Call the method and expect an exception
        with self.assertRaises(ZeptoMailError) as context:
            self.client.send_email(
                from_address="test@example.com",
                to=[self.client.add_recipient("recipient@example.com")],
                subject="Test Email",
                html_body="<p>Test</p>"
            )
        
        # Check the exception message
        self.assertIn("Invalid JSON response", str(context.exception))
        self.assertIn("TM_3301", str(context.exception))
        self.assertIn("SM_101", str(context.exception))
    
    @patch('requests.post')
    def test_send_email_with_all_parameters(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"message_id": "test-id-full"}}
        mock_post.return_value = mock_response
        
        # Create test data
        to_recipients = [self.client.add_recipient("to@example.com", "To Recipient")]
        cc_recipients = [self.client.add_recipient("cc@example.com", "CC Recipient")]
        bcc_recipients = [self.client.add_recipient("bcc@example.com", "BCC Recipient")]
        reply_to = [{"address": "reply@example.com", "name": "Reply To"}]
        
        attachments = [
            self.client.add_attachment_from_content(
                content="base64content", 
                mime_type="application/pdf", 
                name="document.pdf"
            )
        ]
        
        inline_images = [
            self.client.add_inline_image(
                cid="image123", 
                content="base64image", 
                mime_type="image/jpeg"
            )
        ]
        
        mime_headers = {"X-Custom-Header": "Custom Value"}
        
        # Call the method with all parameters
        response = self.client.send_email(
            from_address="sender@example.com",
            from_name="Full Sender",
            to=to_recipients,
            cc=cc_recipients,
            bcc=bcc_recipients,
            reply_to=reply_to,
            subject="Complete Test Email",
            html_body="<p>HTML Content</p>",
            text_body="Plain text content",
            attachments=attachments,
            inline_images=inline_images,
            track_clicks=False,
            track_opens=False,
            client_reference="ref-12345",
            mime_headers=mime_headers
        )
        
        # Assert the response
        self.assertEqual(response, {"data": {"message_id": "test-id-full"}})
        
        # Verify the payload structure
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.zeptomail.eu/v1.1/email")
        
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["from"]["address"], "sender@example.com")
        self.assertEqual(payload["from"]["name"], "Full Sender")
        self.assertEqual(payload["to"], to_recipients)
        self.assertEqual(payload["cc"], cc_recipients)
        self.assertEqual(payload["bcc"], bcc_recipients)
        self.assertEqual(payload["reply_to"], reply_to)
        self.assertEqual(payload["subject"], "Complete Test Email")
        self.assertEqual(payload["htmlbody"], "<p>HTML Content</p>")
        self.assertEqual(payload["textbody"], "Plain text content")
        self.assertEqual(payload["attachments"], attachments)
        self.assertEqual(payload["inline_images"], inline_images)
        self.assertEqual(payload["track_clicks"], False)
        self.assertEqual(payload["track_opens"], False)
        self.assertEqual(payload["client_reference"], "ref-12345")
        self.assertEqual(payload["mime_headers"], mime_headers)
        
    @patch('requests.post')
    def test_send_batch_email(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"batch_id": "batch-123"}}
        mock_post.return_value = mock_response
        
        # Create batch recipients with merge info
        recipients = [
            self.client.add_batch_recipient(
                "recipient1@example.com",
                "Recipient One",
                {"first_name": "Recipient", "last_name": "One"}
            ),
            self.client.add_batch_recipient(
                "recipient2@example.com",
                "Recipient Two",
                {"first_name": "Recipient", "last_name": "Two"}
            )
        ]
        
        # Call the method
        response = self.client.send_batch_email(
            from_address="test@example.com",
            from_name="Sender",
            to=recipients,
            subject="Test Batch Email",
            html_body="<p>Hello {{first_name}} {{last_name}}</p>",
            text_body="Hello {{first_name}} {{last_name}}",
            client_reference="test-batch-123",
            merge_info={"default_name": "User"}
        )
        
        # Assert the response
        self.assertEqual(response, {"data": {"batch_id": "batch-123"}})
        
        # Assert the request was made correctly
        mock_post.assert_called_once()
        
        # Verify the URL used
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.zeptomail.eu/v1.1/email/batch")
        
        # Verify payload structure
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["from"]["address"], "test@example.com")
        self.assertEqual(payload["from"]["name"], "Sender")
        self.assertEqual(len(payload["to"]), 2)
        self.assertEqual(payload["subject"], "Test Batch Email")
        self.assertEqual(payload["htmlbody"], "<p>Hello {{first_name}} {{last_name}}</p>")
        self.assertEqual(payload["textbody"], "Hello {{first_name}} {{last_name}}")
        self.assertEqual(payload["client_reference"], "test-batch-123")
        self.assertEqual(payload["merge_info"], {"default_name": "User"})
    
    def test_add_attachment_from_file_cache(self):
        # Test with name
        result = self.client.add_attachment_from_file_cache("file-cache-key-123", "document.pdf")
        self.assertEqual(result, {"file_cache_key": "file-cache-key-123", "name": "document.pdf"})
        
        # Test without name
        result = self.client.add_attachment_from_file_cache("file-cache-key-123")
        self.assertEqual(result, {"file_cache_key": "file-cache-key-123"})
    
    def test_add_attachment_from_content(self):
        result = self.client.add_attachment_from_content(
            content="base64encodedcontent",
            mime_type="application/pdf",
            name="document.pdf"
        )
        self.assertEqual(result, {
            "content": "base64encodedcontent",
            "mime_type": "application/pdf",
            "name": "document.pdf"
        })
    
    def test_add_inline_image(self):
        # Test with content and mime_type
        result = self.client.add_inline_image(
            cid="image123",
            content="base64encodedimage",
            mime_type="image/jpeg"
        )
        self.assertEqual(result, {
            "cid": "image123",
            "content": "base64encodedimage",
            "mime_type": "image/jpeg"
        })
        
        # Test with file_cache_key
        result = self.client.add_inline_image(
            cid="image123",
            file_cache_key="file-cache-key-123"
        )
        self.assertEqual(result, {
            "cid": "image123",
            "file_cache_key": "file-cache-key-123"
        })
        
        # Test with only cid
        result = self.client.add_inline_image(cid="image123")
        self.assertEqual(result, {"cid": "image123"})
        
    @patch('requests.post')
    def test_send_batch_email_with_all_parameters(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"batch_id": "batch-full-123"}}
        mock_post.return_value = mock_response
        
        # Create test data
        to_recipients = [
            self.client.add_batch_recipient("to@example.com", "To Recipient", {"var": "value"})
        ]
        cc_recipients = [
            self.client.add_batch_recipient("cc@example.com", "CC Recipient")
        ]
        bcc_recipients = [
            self.client.add_batch_recipient("bcc@example.com", "BCC Recipient")
        ]
        
        attachments = [
            self.client.add_attachment_from_content(
                content="base64content", 
                mime_type="application/pdf", 
                name="document.pdf"
            )
        ]
        
        inline_images = [
            self.client.add_inline_image(
                cid="image123", 
                content="base64image", 
                mime_type="image/jpeg"
            )
        ]
        
        mime_headers = {"X-Custom-Header": "Custom Value"}
        
        # Call the method with all parameters
        response = self.client.send_batch_email(
            from_address="sender@example.com",
            from_name="Full Sender",
            to=to_recipients,
            cc=cc_recipients,
            bcc=bcc_recipients,
            subject="Complete Batch Test Email",
            html_body="<p>HTML Content with {{var}}</p>",
            text_body="Plain text content with {{var}}",
            attachments=attachments,
            inline_images=inline_images,
            track_clicks=False,
            track_opens=False,
            client_reference="batch-ref-12345",
            mime_headers=mime_headers,
            merge_info={"default_var": "Default Value"}
        )
        
        # Assert the response
        self.assertEqual(response, {"data": {"batch_id": "batch-full-123"}})
        
        # Verify the payload structure
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.zeptomail.eu/v1.1/email/batch")
        
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["from"]["address"], "sender@example.com")
        self.assertEqual(payload["from"]["name"], "Full Sender")
        self.assertEqual(payload["to"], to_recipients)
        self.assertEqual(payload["cc"], cc_recipients)
        self.assertEqual(payload["bcc"], bcc_recipients)
        self.assertEqual(payload["subject"], "Complete Batch Test Email")
        self.assertEqual(payload["htmlbody"], "<p>HTML Content with {{var}}</p>")
        self.assertEqual(payload["textbody"], "Plain text content with {{var}}")
        self.assertEqual(payload["attachments"], attachments)
        self.assertEqual(payload["inline_images"], inline_images)
        self.assertEqual(payload["track_clicks"], False)
        self.assertEqual(payload["track_opens"], False)
        self.assertEqual(payload["client_reference"], "batch-ref-12345")
        self.assertEqual(payload["mime_headers"], mime_headers)
        self.assertEqual(payload["merge_info"], {"default_var": "Default Value"})
    
    def test_add_batch_recipient(self):
        # Test with name and merge_info
        result = self.client.add_batch_recipient(
            "recipient@example.com",
            "Recipient Name",
            {"first_name": "Recipient", "last_name": "Name", "order_id": "12345"}
        )
        self.assertEqual(result, {
            "email_address": {
                "address": "recipient@example.com",
                "name": "Recipient Name"
            },
            "merge_info": {
                "first_name": "Recipient", 
                "last_name": "Name", 
                "order_id": "12345"
            }
        })
        
        # Test with only address
        result = self.client.add_batch_recipient("recipient@example.com")
        self.assertEqual(result, {
            "email_address": {
                "address": "recipient@example.com"
            }
        })
        
        # Test with address and name but no merge_info
        result = self.client.add_batch_recipient("recipient@example.com", "Recipient Name")
        self.assertEqual(result, {
            "email_address": {
                "address": "recipient@example.com",
                "name": "Recipient Name"
            }
        })
        
if __name__ == '__main__':
    unittest.main()
