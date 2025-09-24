import requests
import json
import base64
from typing import List, Dict, Optional, Any, Union, BinaryIO
import os

from zeptomail.errors import ZeptoMailError

class ZeptoMail:
    """A Python client for interacting with the ZeptoMail API.
    
    Note: This is an unofficial SDK. Namilink Kft is not affiliated with ZeptoMail.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.zeptomail.eu/v1.1"):
        """
        Initialize the ZeptoMail client.

        Args:
            api_key: Your ZeptoMail API key
            base_url: The base URL for the ZeptoMail API (defaults to https://api.zeptomail.eu/v1.1)
        """
        self.api_key = api_key
        self.base_url = base_url
        if not api_key.startswith("Zoho-enczapikey "):
            api_key = f"Zoho-enczapikey {api_key}"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": api_key
        }


    def build_email_dict(self, email: str, name: Optional[str] = None) -> Dict:
        """
        Build a recipient object.

        Args:
            email: Email address of the recipient
            name: Name of the recipient

        Returns:
            Dict containing recipient details
            
        Raises:
            ZeptoMailError: If the email address is invalid
        """
            
        email_dict = {"address": email}
        if name:
            email_dict["name"] = name
            
        return email_dict
    

    def _build_recipient_with_merge_info(self, email: str, name: Optional[str] = None,
                                         merge_info: Optional[Dict] = None) -> Dict:
        """
        Build a recipient object with merge info.

        Args:
            email: Email address of the recipient
            name: Name of the recipient
            merge_info: Dictionary containing merge fields for this recipient

        Returns:
            Dict containing recipient details with merge info
            
        Raises:
            ZeptoMailError: If the email address is invalid
        """
        recipient = {"email_address": self.build_email_dict(email, name)}
        if merge_info:
            recipient["merge_info"] = merge_info
        return recipient

        
    def _handle_response(self, response: requests.Response) -> Dict:
        """
        Handle the API response and check for errors.
        
        Args:
            response: Response object from requests
            
        Returns:
            Parsed response as a dictionary
            
        Raises:
            ZeptoMailError: If the API returns an error
        """
        try:
            response_data = response.json()
        except ValueError:
            raise ZeptoMailError(
                f"Invalid JSON response from API (Status code: {response.status_code})",
                code="TM_3301",
                sub_code="SM_101"
            )
        
        # Check if the response contains an error
        if "error" in response_data:
            error = response_data["error"]
            error_message = error.get("message", "Unknown error")
            error_code = error.get("code", "unknown")
            error_sub_code = error.get("sub_code", None)
            error_details = error.get("details", [])
            request_id = response_data.get("request_id")
            
            # Get solution based on error codes
            solution = ZeptoMailError.get_error_solution(error_code, error_sub_code, error_details)
            if solution:
                error_message = f"{error_message}. {solution}"
            
            raise ZeptoMailError(
                message=error_message,
                code=error_code,
                sub_code=error_sub_code,
                details=error_details,
                request_id=request_id
            )
        if response.status_code != 201:
            raise Exception(
                f"Invalid response from API: {response}",
            )
        
        return response_data
    
    def _ensure_json_serializable(self, obj: Any) -> Any:
        """
        Recursively process an object to ensure it's JSON serializable.
        Converts bytes to base64-encoded strings.
        
        Args:
            obj: The object to process
            
        Returns:
            A JSON serializable version of the object
        """
        if isinstance(obj, dict):
            return {k: self._ensure_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_json_serializable(item) for item in obj]
        elif isinstance(obj, bytes):
            # Convert bytes to base64 encoded string
            return base64.b64encode(obj).decode('utf-8')
        else:
            return obj
            
    def _validate_email_params(self, from_address: str, to: List[Dict], cc: List[Dict], 
                              bcc: List[Dict], html_body: Optional[str], text_body: Optional[str]) -> None:
        """
        Validate required email parameters.
        
        Args:
            from_address: Sender's email address
            to: List of to recipients
            cc: List of cc recipients
            bcc: List of bcc recipients
            html_body: HTML content of the email
            text_body: Plain text content of the email
            
        Raises:
            ZeptoMailError: If any required fields are missing
        """
        if not from_address:
            raise ZeptoMailError(
                "Missing required field: 'from_address' cannot be empty",
                code="VALIDATION_ERROR"
            )
            
        if not (to or cc or bcc):
            raise ZeptoMailError(
                "Missing required field: at least one recipient (to, cc, or bcc) is required",
                code="VALIDATION_ERROR"
            )
            
        if not (html_body or text_body):
            raise ZeptoMailError(
                "Missing required field: either 'html_body' or 'text_body' must be provided",
                code="VALIDATION_ERROR"
            )

    def upload_file(self, file_path: Optional[str] = None, file_data: Optional[bytes] = None, 
                    file_name: Optional[str] = None, content_type: str = "application/octet-stream") -> Dict:
        """
        Upload a file to ZeptoMail's file cache for later use as an attachment.
        
        Args:
            file_path: Path to the file to upload (mutually exclusive with file_data)
            file_data: Binary data of the file to upload (mutually exclusive with file_path)
            file_name: Name for the file in the cache (required if using file_data)
            content_type: MIME type of the file (defaults to application/octet-stream)
            
        Returns:
            Dict containing the file_cache_key and response details
            
        Raises:
            ZeptoMailError: If the upload fails or parameters are invalid
        """
        # Validate input parameters
        if not file_path and not file_data:
            raise ZeptoMailError(
                "Either file_path or file_data must be provided",
                code="VALIDATION_ERROR"
            )
            
        if file_path and file_data:
            raise ZeptoMailError(
                "Only one of file_path or file_data should be provided, not both",
                code="VALIDATION_ERROR"
            )
            
        if file_data and not file_name:
            raise ZeptoMailError(
                "file_name is required when using file_data",
                code="VALIDATION_ERROR"
            )
        
        # Determine file name and prepare data
        if file_path:
            if not os.path.exists(file_path):
                raise ZeptoMailError(
                    f"File not found: {file_path}",
                    code="VALIDATION_ERROR"
                )
            
            name = file_name or os.path.basename(file_path)
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
            except IOError as e:
                raise ZeptoMailError(
                    f"Error reading file: {str(e)}",
                    code="VALIDATION_ERROR"
                )
        else:
            name = file_name
            data = file_data
        
        # Validate file is not empty
        if not data:
            raise ZeptoMailError(
                "File content is empty",
                code="TM_3301"
            )
        
        # Prepare the request
        url = f"{self.base_url}/files"
        params = {"name": name}
        
        # Create headers for file upload (different from regular API calls)
        upload_headers = {
            "Authorization": self.headers["Authorization"],
            "Content-Type": content_type
        }
        
        try:
            response = requests.post(url, params=params, headers=upload_headers, data=data)
            
            # Handle the response
            try:
                response_data = response.json()
            except ValueError:
                raise ZeptoMailError(
                    f"Invalid JSON response from file upload API (Status code: {response.status_code})",
                    code="TM_3301"
                )
            
            # Check for errors in the response
            if response.status_code != 201 or "error" in response_data:
                if "error" in response_data:
                    error = response_data["error"]
                    error_message = error.get("message", "Unknown error")
                    error_code = error.get("code", "unknown")
                    error_sub_code = error.get("sub_code", None)
                    error_details = error.get("details", [])
                    request_id = response_data.get("request_id")
                    
                    # Get solution based on error codes
                    solution = ZeptoMailError.get_error_solution(error_code, error_sub_code, error_details)
                    if solution:
                        error_message = f"{error_message}. {solution}"
                    
                    raise ZeptoMailError(
                        message=error_message,
                        code=error_code,
                        sub_code=error_sub_code,
                        details=error_details,
                        request_id=request_id
                    )
                else:
                    raise ZeptoMailError(
                        f"File upload failed with status code: {response.status_code}",
                        code="UPLOAD_ERROR"
                    )
            
            return response_data
            
        except requests.RequestException as e:
            raise ZeptoMailError(
                f"Network error during file upload: {str(e)}",
                code="NETWORK_ERROR"
            )
    
    def send_email(self,
                   from_address: str,
                   from_name: Optional[str] = None,
                   to: List[Dict] = None,
                   cc: List[Dict] = None,
                   bcc: List[Dict] = None,
                   reply_to: List[Dict] = None,
                   subject: str = "",
                   html_body: Optional[str] = None,
                   text_body: Optional[str] = None,
                   attachments: List[Dict] = None,
                   inline_images: List[Dict] = None,
                   track_clicks: bool = True,
                   track_opens: bool = True,
                   client_reference: Optional[str] = None,
                   mime_headers: Optional[Dict] = None) -> Dict:
        """
        Send a single email using the ZeptoMail API.

        Args:
            from_email: Sender's Email address
            from_name: Sender's name
            to: List of recipient dictionaries
            cc: List of cc recipient dictionaries
            bcc: List of bcc recipient dictionaries
            reply_to: List of reply-to dictionaries
            subject: Email subject
            html_body: HTML content of the email
            text_body: Plain text content of the email
            attachments: List of attachment dictionaries
            inline_images: List of inline image dictionaries
            track_clicks: Whether to track clicks
            track_opens: Whether to track opens
            client_reference: Client reference identifier
            mime_headers: Additional MIME headers

        Returns:
            API response as a dictionary
            
        Raises:
            ZeptoMailError: If required fields are missing or API returns an error
        """
        # Validate required fields
        self._validate_email_params(from_address, to, cc, bcc, html_body, text_body)
        
        url = f"{self.base_url}/email"

        payload = {
            "from": self.build_email_dict(from_address, from_name),
            "subject": subject
        }

        # Add recipients
        if to:
            payload["to"] = to

        if cc:
            payload["cc"] = cc

        if bcc:
            payload["bcc"] = bcc

        if reply_to:
            payload["reply_to"] = reply_to

        # Add content
        if html_body:
            payload["htmlbody"] = html_body

        if text_body:
            payload["textbody"] = text_body

        # Add tracking options
        payload["track_clicks"] = track_clicks
        payload["track_opens"] = track_opens

        # Add optional parameters
        if client_reference:
            payload["client_reference"] = client_reference

        if mime_headers:
            payload["mime_headers"] = mime_headers

        if attachments:
            payload["attachments"] = attachments

        if inline_images:
            payload["inline_images"] = inline_images

        # Ensure payload is JSON serializable by encoding any bytes objects to base64 strings
        serializable_payload = self._ensure_json_serializable(payload)
        response = requests.post(url, headers=self.headers, data=json.dumps(serializable_payload))
        return self._handle_response(response)

    def send_batch_email(self,
                         from_address: str,
                         from_name: Optional[str] = None,
                         to: List[Dict] = None,
                         cc: List[Dict] = None,
                         bcc: List[Dict] = None,
                         subject: str = "",
                         html_body: Optional[str] = None,
                         text_body: Optional[str] = None,
                         attachments: List[Dict] = None,
                         inline_images: List[Dict] = None,
                         track_clicks: bool = True,
                         track_opens: bool = True,
                         client_reference: Optional[str] = None,
                         mime_headers: Optional[Dict] = None,
                         merge_info: Optional[Dict] = None) -> Dict:
        """
        Send a batch email using the ZeptoMail API.

        Args:
            from_email: Sender's Email address
            from_name: Sender's name
            to: List of recipient dictionaries with optional merge_info
            cc: List of cc recipient dictionaries
            bcc: List of bcc recipient dictionaries
            subject: Email subject
            html_body: HTML content of the email
            text_body: Plain text content of the email
            attachments: List of attachment dictionaries
            inline_images: List of inline image dictionaries
            track_clicks: Whether to track clicks
            track_opens: Whether to track opens
            client_reference: Client reference identifier
            mime_headers: Additional MIME headers
            merge_info: Global merge info for recipients without specific merge info

        Returns:
            API response as a dictionary
            
        Raises:
            ZeptoMailError: If required fields are missing or API returns an error
        """
        # Validate required fields
        self._validate_email_params(from_address, to, cc, bcc, html_body, text_body)
        
        url = f"{self.base_url}/email/batch"

        payload = {
            "from": self.build_email_dict(from_address, from_name),
            "subject": subject
        }

        # Add recipients
        if to:
            payload["to"] = to

        if cc:
            payload["cc"] = cc

        if bcc:
            payload["bcc"] = bcc

        # Add content
        if html_body:
            payload["htmlbody"] = html_body

        if text_body:
            payload["textbody"] = text_body

        # Add tracking options
        payload["track_clicks"] = track_clicks
        payload["track_opens"] = track_opens

        # Add optional parameters
        if client_reference:
            payload["client_reference"] = client_reference

        if mime_headers:
            payload["mime_headers"] = mime_headers

        if attachments:
            payload["attachments"] = attachments

        if inline_images:
            payload["inline_images"] = inline_images

        if merge_info:
            payload["merge_info"] = merge_info

        # Ensure payload is JSON serializable by encoding any bytes objects to base64 strings
        serializable_payload = self._ensure_json_serializable(payload)
        response = requests.post(url, headers=self.headers, data=json.dumps(serializable_payload))
        return self._handle_response(response)

    # Helper methods for common operations

    def add_recipient(self, email: str, name: Optional[str] = None) -> Dict:
        """
        Create a recipient object for use in to, cc, bcc lists.

        Args:
            email: Email address
            name: Recipient name

        Returns:
            Recipient dictionary with format {"email_address": {"email": email, "name": name}}
        """
        return {"email_address": self.build_email_dict(email, name)}

    def add_batch_recipient(self, email: str, name: Optional[str] = None,
                            merge_info: Optional[Dict] = None) -> Dict:
        """
        Create a batch recipient object with merge info.

        Args:
            email: Email address
            name: Recipient name
            merge_info: Merge fields for this recipient

        Returns:
            Recipient dictionary with format {"email_address": {"email": email, "name": name, "merge_info": {...}}}
        """
        recipient = {"address": email}
        if name:
            recipient["name"] = name
        if merge_info:
            recipient["merge_info"] = merge_info
        return {"email_address":recipient}

    def add_attachment_from_file_cache(self, file_cache_key: str, name: Optional[str] = None) -> Dict:
        """
        Add an attachment using a file cache key.

        Args:
            file_cache_key: File cache key from ZeptoMail
            name: Optional name for the file

        Returns:
            Attachment dictionary
        """
        attachment = {"file_cache_key": file_cache_key}
        if name:
            attachment["name"] = name
        return attachment

    def add_attachment_from_content(self, content: str, mime_type: str, name: str) -> Dict:
        """
        Add an attachment using base64 encoded content.

        Args:
            content: Base64 encoded content
            mime_type: MIME type of the content
            name: Name for the file

        Returns:
            Attachment dictionary
        """
        return {
            "content": content,
            "mime_type": mime_type,
            "name": name
        }

    def add_inline_image(self, cid: str, content: Optional[str] = None,
                         mime_type: Optional[str] = None,
                         file_cache_key: Optional[str] = None) -> Dict:
        """
        Add an inline image to the email.

        Args:
            cid: Content ID to reference in HTML
            content: Base64 encoded content
            mime_type: MIME type of the content
            file_cache_key: File cache key from ZeptoMail

        Returns:
            Inline image dictionary
        """
        inline_image = {"cid": cid}

        if content and mime_type:
            inline_image["content"] = content
            inline_image["mime_type"] = mime_type

        if file_cache_key:
            inline_image["file_cache_key"] = file_cache_key

        return inline_image
