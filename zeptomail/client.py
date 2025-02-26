import requests
import json
from typing import List, Dict, Optional

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

    def _build_email_address(self, address: str, name: Optional[str] = None) -> Dict:
        """
        Build an email address object.

        Args:
            address: Email address
            name: Name associated with the email address

        Returns:
            Dict containing email address details
        """
        email_obj = {"address": address}
        if name:
            email_obj["name"] = name
        return email_obj

    def _build_recipient(self, address: str, name: Optional[str] = None) -> Dict:
        """
        Build a recipient object.

        Args:
            address: Email address of the recipient
            name: Name of the recipient

        Returns:
            Dict containing recipient details
        """
        recipient = {"email_address": self._build_email_address(address, name)}
        return recipient

    def _build_recipient_with_merge_info(self, address: str, name: Optional[str] = None,
                                         merge_info: Optional[Dict] = None) -> Dict:
        """
        Build a recipient object with merge info.

        Args:
            address: Email address of the recipient
            name: Name of the recipient
            merge_info: Dictionary containing merge fields for this recipient

        Returns:
            Dict containing recipient details with merge info
        """
        recipient = self._build_recipient(address, name)
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
            solution = self._get_error_solution(error_code, error_sub_code, error_details)
            if solution:
                error_message = f"{error_message}. {solution}"
            
            raise ZeptoMailError(
                message=error_message,
                code=error_code,
                sub_code=error_sub_code,
                details=error_details,
                request_id=request_id
            )
        
        return response_data
    
    def _get_error_solution(self, code: str, sub_code: str, details: List[Dict]) -> Optional[str]:
        """
        Get a solution message based on error codes.
        
        Args:
            code: The error code
            sub_code: The error sub-code
            details: Error details
            
        Returns:
            A solution message or None
        """
        # Map of error codes to solutions
        error_solutions = {
            "TM_3201": {
                "GE_102": {
                    "subject": "Set a non-empty subject for your email.",
                    "from": "Add the mandatory 'from' field with a valid email address.",
                    "to": "Add at least one recipient using 'to', 'cc', or 'bcc' fields.",
                    "Mail Template Key": "Add the mandatory 'Mail Template Key' field."
                }
            },
            "TM_3301": {
                "SM_101": "Check your API request syntax for valid JSON format.",
                "SM_120": "Ensure the attachment MIME type matches the actual file content."
            },
            "TM_3501": {
                "UE_106": "Use a valid File Cache Key from your Mail Agent's File Cache tab.",
                "MTR_101": "Use a valid Template Key from your Mail Agent.",
                "LE_101": "Your credits have expired. Purchase new credits from the ZeptoMail Subscription page."
            },
            "TM_3601": {
                "SERR_156": "Add your sending IP to the allowed IPs list in settings.",
                "SM_133": "Your trial sending limit is exceeded. Get your account reviewed to continue.",
                "SMI_115": "Daily sending limit reached. Try again tomorrow.",
                "AE_101": "Your account is blocked. Contact ZeptoMail support."
            },
            "TM_4001": {
                "SM_111": "Use a sender address with a domain that is verified in your Mail Agent.",
                "SM_113": "Provide valid values for all required fields.",
                "SM_128": "Your account needs to be reviewed. Get your account approved before sending emails.",
                "SERR_157": "Use a valid Sendmail token from your Mail Agent configuration settings."
            },
            "TM_5001": {
                "LE_102": "Your credits are exhausted. Purchase new credits from the ZeptoMail Subscription page."
            },
            "TM_8001": {
                "SM_127": "Reduce the number of attachments to 60 or fewer.",
                "SM_129": "Ensure all name fields are under 250 characters, subject is under 500 characters, attachment size is under 15MB, and attachment filenames are under 150 characters."
            }
        }
        
        # Check if we have a solution for this error code
        if code in error_solutions:
            code_solutions = error_solutions[code]
            
            # If we have a sub-code specific solution
            if sub_code in code_solutions:
                sub_code_solution = code_solutions[sub_code]
                
                # If the sub-code solution is a string, return it directly
                if isinstance(sub_code_solution, str):
                    return sub_code_solution
                
                # If it's a dict, try to find a more specific solution based on details
                elif isinstance(sub_code_solution, dict) and details:
                    for detail in details:
                        target = detail.get("target", "")
                        if target in sub_code_solution:
                            return sub_code_solution[target]
                    
                    # If no specific target match, return the first solution
                    return next(iter(sub_code_solution.values()), None)
        
        return None
    
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
            from_address: Sender's email address
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
        """
        url = f"{self.base_url}/email"

        payload = {
            "from": self._build_email_address(from_address, from_name),
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

        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
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
            from_address: Sender's email address
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
        """
        url = f"{self.base_url}/email/batch"

        payload = {
            "from": self._build_email_address(from_address, from_name),
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

        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        return self._handle_response(response)

    # Helper methods for common operations

    def add_recipient(self, address: str, name: Optional[str] = None) -> Dict:
        """
        Create a recipient object for use in to, cc, bcc lists.

        Args:
            address: Email address
            name: Recipient name

        Returns:
            Recipient dictionary
        """
        return self._build_recipient(address, name)

    def add_batch_recipient(self, address: str, name: Optional[str] = None,
                            merge_info: Optional[Dict] = None) -> Dict:
        """
        Create a batch recipient object with merge info.

        Args:
            address: Email address
            name: Recipient name
            merge_info: Merge fields for this recipient

        Returns:
            Recipient dictionary with merge info
        """
        return self._build_recipient_with_merge_info(address, name, merge_info)

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
