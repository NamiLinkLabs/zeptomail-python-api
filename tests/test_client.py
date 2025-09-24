import unittest
from unittest.mock import patch, Mock
import json
import base64
import requests
from zeptomail.client import ZeptoMail
from zeptomail.errors import ZeptoMailError

class TestZeptoMail(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.client = ZeptoMail(self.api_key)
        
    def test_init(self):
        """Test client initialization with different API key formats"""
        # Test with plain API key
        client = ZeptoMail("test_api_key")
        self.assertEqual(client.api_key, "test_api_key")
        self.assertEqual(client.headers["Authorization"], "Zoho-enczapikey test_api_key")
        
        # Test with prefixed API key
        client = ZeptoMail("Zoho-enczapikey prefixed_key")
        self.assertEqual(client.api_key, "Zoho-enczapikey prefixed_key")
        self.assertEqual(client.headers["Authorization"], "Zoho-enczapikey prefixed_key")
        
        # Test with custom base URL
        client = ZeptoMail("test_api_key", base_url="https://custom.api.url")
        self.assertEqual(client.base_url, "https://custom.api.url")
    
    def test_build_email_dict(self):
        """Test building email dictionaries"""
        # Test with email only
        email_dict = self.client.build_email_dict("test@example.com")
        self.assertEqual(email_dict, {"address": "test@example.com"})
        
        # Test with email and name
        email_dict = self.client.build_email_dict("test@example.com", "Test User")
        self.assertEqual(email_dict, {"address": "test@example.com", "name": "Test User"})
    
    def test_build_recipient_with_merge_info(self):
        """Test building recipient with merge info"""
        # Test with email only
        recipient = self.client._build_recipient_with_merge_info("test@example.com")
        self.assertEqual(recipient, {
            "email_address": {"address": "test@example.com"}
        })
        
        # Test with email and name
        recipient = self.client._build_recipient_with_merge_info("test@example.com", "Test User")
        self.assertEqual(recipient, {
            "email_address": {"address": "test@example.com", "name": "Test User"}
        })
        
        # Test with merge info
        merge_info = {"first_name": "Test", "last_name": "User"}
        recipient = self.client._build_recipient_with_merge_info(
            "test@example.com", "Test User", merge_info
        )
        self.assertEqual(recipient, {
            "email_address": {"address": "test@example.com", "name": "Test User"},
            "merge_info": {"first_name": "Test", "last_name": "User"}
        })
    
    def test_ensure_json_serializable(self):
        """Test JSON serialization of different data types"""
        # Test with simple types
        self.assertEqual(self.client._ensure_json_serializable("test"), "test")
        self.assertEqual(self.client._ensure_json_serializable(123), 123)
        
        # Test with bytes
        bytes_data = b"test bytes"
        expected = base64.b64encode(bytes_data).decode('utf-8')
        self.assertEqual(self.client._ensure_json_serializable(bytes_data), expected)
        
        # Test with nested structures
        complex_data = {
            "string": "test",
            "number": 123,
            "bytes": b"test bytes",
            "list": ["test", 123, b"more bytes"],
            "nested": {
                "bytes": b"nested bytes"
            }
        }
        expected = {
            "string": "test",
            "number": 123,
            "bytes": base64.b64encode(b"test bytes").decode('utf-8'),
            "list": ["test", 123, base64.b64encode(b"more bytes").decode('utf-8')],
            "nested": {
                "bytes": base64.b64encode(b"nested bytes").decode('utf-8')
            }
        }
        self.assertEqual(self.client._ensure_json_serializable(complex_data), expected)
    
    @patch('requests.post')
    def test_handle_response_success(self, mock_post):
        """Test successful API response handling"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": "test_data"}
        
        result = self.client._handle_response(mock_response)
        self.assertEqual(result, {"data": "test_data"})
    
    @patch('requests.post')
    def test_handle_response_error(self, mock_post):
        """Test error API response handling"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": "TM_3201",
                "sub_code": "GE_102",
                "message": "Error message",
                "details": [{"target": "subject", "message": "Subject is required"}]
            },
            "request_id": "test_request_id"
        }
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client._handle_response(mock_response)
        
        error = context.exception
        self.assertEqual(error.code, "TM_3201")
        self.assertEqual(error.sub_code, "GE_102")
        self.assertEqual(error.request_id, "test_request_id")
        self.assertIn("Subject is required", str(error))
    
    @patch('requests.post')
    def test_handle_response_invalid_json(self, mock_post):
        """Test handling invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client._handle_response(mock_response)
        
        error = context.exception
        self.assertEqual(error.code, "TM_3301")
        self.assertEqual(error.sub_code, "SM_101")
        self.assertIn("Invalid JSON response", str(error))
    
    @patch('requests.post')
    def test_handle_response_non_201(self, mock_post):
        """Test handling non-201 response without error object"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        
        with self.assertRaises(Exception) as context:
            self.client._handle_response(mock_response)
        
        self.assertIn("Invalid response from API", str(context.exception))
    
    @patch('requests.post')
    def test_send_email_success(self, mock_post):
        """Test successful email sending"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": {"message_id": "test_id"}}
        mock_post.return_value = mock_response
        
        result = self.client.send_email(
            from_address="from@example.com",
            from_name="Sender",
            to=[{"address": "to@example.com", "name": "Recipient"}],
            subject="Test Subject",
            html_body="<p>Test Body</p>"
        )
        
        self.assertEqual(result, {"data": {"message_id": "test_id"}})
        mock_post.assert_called_once()
        
        # Verify the payload
        call_args = mock_post.call_args
        url = call_args[0][0]
        headers = call_args[1]["headers"]
        payload = json.loads(call_args[1]["data"])
        
        self.assertEqual(url, "https://api.zeptomail.eu/v1.1/email")
        self.assertEqual(headers["Authorization"], "Zoho-enczapikey test_api_key")
        self.assertEqual(payload["from"], {"address": "from@example.com", "name": "Sender"})
        self.assertEqual(payload["to"], [{"address": "to@example.com", "name": "Recipient"}])
        self.assertEqual(payload["subject"], "Test Subject")
        self.assertEqual(payload["htmlbody"], "<p>Test Body</p>")
    
    @patch('requests.post')
    def test_send_email_with_all_options(self, mock_post):
        """Test email sending with all optional parameters"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": {"message_id": "test_id"}}
        mock_post.return_value = mock_response
        
        # Create test data for all optional parameters
        cc_recipients = [{"address": "cc@example.com", "name": "CC Recipient"}]
        bcc_recipients = [{"address": "bcc@example.com", "name": "BCC Recipient"}]
        reply_to = [{"address": "reply@example.com", "name": "Reply Contact"}]
        attachments = [{"file_cache_key": "test_key", "name": "test.pdf"}]
        inline_images = [{"cid": "image1", "file_cache_key": "image_key"}]
        client_reference = "test-reference-123"
        mime_headers = {"X-Custom-Header": "Custom Value"}
        
        result = self.client.send_email(
            from_address="from@example.com",
            from_name="Sender",
            to=[{"address": "to@example.com", "name": "Recipient"}],
            cc=cc_recipients,
            bcc=bcc_recipients,
            reply_to=reply_to,
            subject="Test Subject",
            html_body="<p>Test HTML</p>",
            text_body="Test plain text",
            attachments=attachments,
            inline_images=inline_images,
            track_clicks=False,
            track_opens=False,
            client_reference=client_reference,
            mime_headers=mime_headers
        )
        
        self.assertEqual(result, {"data": {"message_id": "test_id"}})
        
        # Verify the payload includes all optional parameters
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]["data"])
        
        # Check all optional parameters are included correctly
        self.assertEqual(payload["cc"], cc_recipients)
        self.assertEqual(payload["bcc"], bcc_recipients)
        self.assertEqual(payload["reply_to"], reply_to)
        self.assertEqual(payload["htmlbody"], "<p>Test HTML</p>")
        self.assertEqual(payload["textbody"], "Test plain text")
        self.assertEqual(payload["track_clicks"], False)
        self.assertEqual(payload["track_opens"], False)
        self.assertEqual(payload["client_reference"], client_reference)
        self.assertEqual(payload["mime_headers"], mime_headers)
        self.assertEqual(payload["attachments"], attachments)
        self.assertEqual(payload["inline_images"], inline_images)
    
    def test_validate_email_params(self):
        """Test the email parameter validation method"""
        # Test missing from_address
        with self.assertRaises(ZeptoMailError) as context:
            self.client._validate_email_params(
                from_address="",
                to=[{"address": "to@example.com"}],
                cc=None,
                bcc=None,
                html_body="<p>Test</p>",
                text_body=None
            )
        self.assertEqual(context.exception.code, "VALIDATION_ERROR")
        self.assertIn("from_address", str(context.exception))
        
        # Test missing recipients
        with self.assertRaises(ZeptoMailError) as context:
            self.client._validate_email_params(
                from_address="from@example.com",
                to=None,
                cc=None,
                bcc=None,
                html_body="<p>Test</p>",
                text_body=None
            )
        self.assertEqual(context.exception.code, "VALIDATION_ERROR")
        self.assertIn("recipient", str(context.exception))
        
        # Test missing body
        with self.assertRaises(ZeptoMailError) as context:
            self.client._validate_email_params(
                from_address="from@example.com",
                to=[{"address": "to@example.com"}],
                cc=None,
                bcc=None,
                html_body=None,
                text_body=None
            )
        self.assertEqual(context.exception.code, "VALIDATION_ERROR")
        self.assertIn("body", str(context.exception))
    
    @patch('requests.post')
    def test_send_email_validation_errors(self, mock_post):
        """Test validation errors when sending email"""
        # Test missing from_address
        with self.assertRaises(ZeptoMailError) as context:
            self.client.send_email(
                from_address="",
                to=[{"address": "to@example.com"}],
                html_body="<p>Test</p>"
            )
        self.assertEqual(context.exception.code, "VALIDATION_ERROR")
        self.assertIn("from_address", str(context.exception))
        
        # Test missing recipients
        with self.assertRaises(ZeptoMailError) as context:
            self.client.send_email(
                from_address="from@example.com",
                to=None,
                html_body="<p>Test</p>"
            )
        self.assertEqual(context.exception.code, "VALIDATION_ERROR")
        self.assertIn("recipient", str(context.exception))
        
        # Test missing body
        with self.assertRaises(ZeptoMailError) as context:
            self.client.send_email(
                from_address="from@example.com",
                to=[{"address": "to@example.com"}],
                html_body=None,
                text_body=None
            )
        self.assertEqual(context.exception.code, "VALIDATION_ERROR")
        self.assertIn("body", str(context.exception))
    
    @patch('requests.post')
    def test_send_batch_email(self, mock_post):
        """Test batch email sending"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": {"batch_id": "test_batch_id"}}
        mock_post.return_value = mock_response
        
        result = self.client.send_batch_email(
            from_address="from@example.com",
            from_name="Sender",
            to=[
                {"address": "to1@example.com", "name": "Recipient 1", "merge_info": {"name": "John"}},
                {"address": "to2@example.com", "name": "Recipient 2", "merge_info": {"name": "Jane"}}
            ],
            subject="Test Subject",
            html_body="<p>Hello {{name}}</p>",
            merge_info={"default": "Friend"}
        )
        
        self.assertEqual(result, {"data": {"batch_id": "test_batch_id"}})
        mock_post.assert_called_once()
        
        # Verify the payload
        call_args = mock_post.call_args
        url = call_args[0][0]
        payload = json.loads(call_args[1]["data"])
        
        self.assertEqual(url, "https://api.zeptomail.eu/v1.1/email/batch")
        self.assertEqual(payload["from"], {"address": "from@example.com", "name": "Sender"})
        self.assertEqual(payload["to"], [
            {"address": "to1@example.com", "name": "Recipient 1", "merge_info": {"name": "John"}},
            {"address": "to2@example.com", "name": "Recipient 2", "merge_info": {"name": "Jane"}}
        ])
        self.assertEqual(payload["merge_info"], {"default": "Friend"})
        
    @patch('requests.post')
    def test_send_batch_email_with_all_options(self, mock_post):
        """Test batch email sending with all optional parameters"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": {"batch_id": "test_batch_id"}}
        mock_post.return_value = mock_response
        
        # Create test data for all optional parameters
        cc_recipients = [{"address": "cc@example.com", "name": "CC Recipient"}]
        bcc_recipients = [{"address": "bcc@example.com", "name": "BCC Recipient"}]
        attachments = [{"file_cache_key": "test_key", "name": "test.pdf"}]
        inline_images = [{"cid": "image1", "file_cache_key": "image_key"}]
        client_reference = "test-reference-123"
        mime_headers = {"X-Custom-Header": "Custom Value"}
        
        result = self.client.send_batch_email(
            from_address="from@example.com",
            from_name="Sender",
            to=[{"address": "to@example.com", "name": "Recipient"}],
            cc=cc_recipients,
            bcc=bcc_recipients,
            subject="Test Subject",
            html_body="<p>Test HTML</p>",
            text_body="Test plain text",
            attachments=attachments,
            inline_images=inline_images,
            track_clicks=False,
            track_opens=False,
            client_reference=client_reference,
            mime_headers=mime_headers,
            merge_info={"default": "Friend"}
        )
        
        self.assertEqual(result, {"data": {"batch_id": "test_batch_id"}})
        
        # Verify the payload includes all optional parameters
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]["data"])
        
        # Check all optional parameters are included correctly
        self.assertEqual(payload["cc"], cc_recipients)
        self.assertEqual(payload["bcc"], bcc_recipients)
        self.assertEqual(payload["htmlbody"], "<p>Test HTML</p>")
        self.assertEqual(payload["textbody"], "Test plain text")
        self.assertEqual(payload["track_clicks"], False)
        self.assertEqual(payload["track_opens"], False)
        self.assertEqual(payload["client_reference"], client_reference)
        self.assertEqual(payload["mime_headers"], mime_headers)
        self.assertEqual(payload["attachments"], attachments)
        self.assertEqual(payload["inline_images"], inline_images)
        self.assertEqual(payload["merge_info"], {"default": "Friend"})
    
    def test_helper_methods(self):
        """Test helper methods for creating recipients and attachments"""
        # Test add_recipient
        recipient = self.client.add_recipient("test@example.com", "Test User")
        self.assertEqual(recipient, {'email_address': {'address': 'test@example.com', 'name': 'Test User'}})
        
        # Test add_batch_recipient
        batch_recipient = self.client.add_batch_recipient(
            "test@example.com", "Test User", {"var1": "value1"}
        )
        self.assertEqual(batch_recipient, {'email_address': {'address': 'test@example.com', 'merge_info': {'var1': 'value1'}, 'name': 'Test User'}})
        
        # Test add_attachment_from_file_cache
        attachment = self.client.add_attachment_from_file_cache("cache_key", "file.pdf")
        self.assertEqual(attachment, {"file_cache_key": "cache_key", "name": "file.pdf"})
        
        # Test add_attachment_from_content
        attachment = self.client.add_attachment_from_content(
            "base64content", "application/pdf", "file.pdf"
        )
        self.assertEqual(attachment, {
            "content": "base64content",
            "mime_type": "application/pdf",
            "name": "file.pdf"
        })
        
        # Test add_inline_image with content
        inline_image = self.client.add_inline_image(
            "image_cid", "base64content", "image/png"
        )
        self.assertEqual(inline_image, {
            "cid": "image_cid",
            "content": "base64content",
            "mime_type": "image/png"
        })
        
        # Test add_inline_image with file_cache_key
        inline_image = self.client.add_inline_image("image_cid", file_cache_key="cache_key")
        self.assertEqual(inline_image, {
            "cid": "image_cid",
            "file_cache_key": "cache_key"
        })

    @patch('requests.post')
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_upload_file_with_file_path_success(self, mock_open, mock_exists, mock_post):
        """Test successful file upload using file_path"""
        # Mock file system
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = b"test file content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"file_cache_key": "test_cache_key"}
        mock_post.return_value = mock_response
        
        result = self.client.upload_file(
            file_path="/path/to/test.pdf",
            content_type="application/pdf"
        )
        
        self.assertEqual(result, {"file_cache_key": "test_cache_key"})
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        url = call_args[0][0]
        params = call_args[1]["params"]
        headers = call_args[1]["headers"]
        data = call_args[1]["data"]
        
        self.assertEqual(url, "https://api.zeptomail.eu/v1.1/files")
        self.assertEqual(params, {"name": "test.pdf"})
        self.assertEqual(headers["Authorization"], "Zoho-enczapikey test_api_key")
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(data, b"test file content")
    
    @patch('requests.post')
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_upload_file_with_file_path_and_custom_name(self, mock_open, mock_exists, mock_post):
        """Test file upload with custom file name"""
        # Mock file system
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = b"test file content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"file_cache_key": "test_cache_key"}
        mock_post.return_value = mock_response
        
        result = self.client.upload_file(
            file_path="/path/to/original.pdf",
            file_name="custom_name.pdf",
            content_type="application/pdf"
        )
        
        self.assertEqual(result, {"file_cache_key": "test_cache_key"})
        
        # Verify custom name is used
        call_args = mock_post.call_args
        params = call_args[1]["params"]
        self.assertEqual(params, {"name": "custom_name.pdf"})
    
    @patch('requests.post')
    def test_upload_file_with_file_data_success(self, mock_post):
        """Test successful file upload using file_data"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"file_cache_key": "test_cache_key"}
        mock_post.return_value = mock_response
        
        file_data = b"test file content"
        result = self.client.upload_file(
            file_data=file_data,
            file_name="test.pdf",
            content_type="application/pdf"
        )
        
        self.assertEqual(result, {"file_cache_key": "test_cache_key"})
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        url = call_args[0][0]
        params = call_args[1]["params"]
        headers = call_args[1]["headers"]
        data = call_args[1]["data"]
        
        self.assertEqual(url, "https://api.zeptomail.eu/v1.1/files")
        self.assertEqual(params, {"name": "test.pdf"})
        self.assertEqual(headers["Authorization"], "Zoho-enczapikey test_api_key")
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(data, file_data)
    
    def test_upload_file_validation_no_params(self):
        """Test validation error when neither file_path nor file_data provided"""
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file()
        
        error = context.exception
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertIn("Either file_path or file_data must be provided", str(error))
    
    def test_upload_file_validation_both_params(self):
        """Test validation error when both file_path and file_data provided"""
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(
                file_path="/path/to/file.pdf",
                file_data=b"test data"
            )
        
        error = context.exception
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertIn("Only one of file_path or file_data should be provided", str(error))
    
    def test_upload_file_validation_file_data_no_name(self):
        """Test validation error when file_data provided without file_name"""
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_data=b"test data")
        
        error = context.exception
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertIn("file_name is required when using file_data", str(error))
    
    @patch('os.path.exists')
    def test_upload_file_file_not_found(self, mock_exists):
        """Test error when file doesn't exist"""
        mock_exists.return_value = False
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_path="/nonexistent/file.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertIn("File not found: /nonexistent/file.pdf", str(error))
    
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_upload_file_io_error(self, mock_open, mock_exists):
        """Test error when file cannot be read"""
        mock_exists.return_value = True
        mock_open.side_effect = IOError("Permission denied")
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_path="/path/to/file.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertIn("Error reading file: Permission denied", str(error))
    
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_upload_file_empty_file_path(self, mock_open, mock_exists):
        """Test error when file is empty (file_path)"""
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = b""  # Return empty bytes, not empty string
        mock_open.return_value.__enter__.return_value = mock_file
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_path="/path/to/empty.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "TM_3301")
        self.assertIn("File content is empty", str(error))
    
    def test_upload_file_empty_file_data(self):
        """Test error when file_data is empty"""
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_data=b"", file_name="empty.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "VALIDATION_ERROR")
    
    @patch('requests.post')
    def test_upload_file_api_error_response(self, mock_post):
        """Test handling API error response"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": "TM_3201",
                "sub_code": "GE_102",
                "message": "File upload failed",
                "details": [{"target": "file", "message": "File too large"}]
            },
            "request_id": "test_request_id"
        }
        mock_post.return_value = mock_response
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_data=b"test data", file_name="test.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "TM_3201")
        self.assertEqual(error.sub_code, "GE_102")
        self.assertEqual(error.request_id, "test_request_id")
        self.assertIn("File upload failed", str(error))
    
    @patch('requests.post')
    def test_upload_file_invalid_json_response(self, mock_post):
        """Test handling invalid JSON response from upload API"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_data=b"test data", file_name="test.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "TM_3301")
        self.assertIn("Invalid JSON response from file upload API", str(error))
    
    @patch('requests.post')
    def test_upload_file_non_201_status_without_error(self, mock_post):
        """Test handling non-201 status code without error object"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"some": "data"}
        mock_post.return_value = mock_response
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_data=b"test data", file_name="test.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "UPLOAD_ERROR")
        self.assertIn("File upload failed with status code: 500", str(error))
    
    @patch('requests.post')
    def test_upload_file_network_error(self, mock_post):
        """Test handling network errors during upload"""
        mock_post.side_effect = requests.RequestException("Network timeout")
        
        with self.assertRaises(ZeptoMailError) as context:
            self.client.upload_file(file_data=b"test data", file_name="test.pdf")
        
        error = context.exception
        self.assertEqual(error.code, "NETWORK_ERROR")
        self.assertIn("Network error during file upload: Network timeout", str(error))
    
    @patch('requests.post')
    def test_upload_file_default_content_type(self, mock_post):
        """Test upload with default content type"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"file_cache_key": "test_cache_key"}
        mock_post.return_value = mock_response
        
        result = self.client.upload_file(
            file_data=b"test data",
            file_name="test.bin"
        )
        
        self.assertEqual(result, {"file_cache_key": "test_cache_key"})
        
        # Verify default content type is used
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        self.assertEqual(headers["Content-Type"], "application/octet-stream")
    
    @patch('requests.post')
    @patch('os.path.exists')
    @patch('os.path.basename')
    @patch('builtins.open', create=True)
    def test_upload_file_basename_extraction(self, mock_open, mock_basename, mock_exists, mock_post):
        """Test that basename is correctly extracted from file path"""
        # Mock file system
        mock_exists.return_value = True
        mock_basename.return_value = "extracted_name.pdf"
        mock_file = Mock()
        mock_file.read.return_value = b"test file content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"file_cache_key": "test_cache_key"}
        mock_post.return_value = mock_response
        
        result = self.client.upload_file(file_path="/long/path/to/extracted_name.pdf")
        
        self.assertEqual(result, {"file_cache_key": "test_cache_key"})
        
        # Verify basename was called and used
        mock_basename.assert_called_once_with("/long/path/to/extracted_name.pdf")
        call_args = mock_post.call_args
        params = call_args[1]["params"]
        self.assertEqual(params, {"name": "extracted_name.pdf"})

if __name__ == '__main__':
    unittest.main()
