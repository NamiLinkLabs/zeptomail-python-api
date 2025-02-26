import requests
import json
from typing import List, Dict, Union, Optional


class ZeptoMail:
    """A Python client for interacting with the ZeptoMail API."""

    def __init__(self, api_key: str, base_url: str = "https://api.zeptomail.eu/v1.1"):
        """
        Initialize the ZeptoMail client.

        Args:
            api_key: Your ZeptoMail API key
            base_url: The base URL for the ZeptoMail API (defaults to https://api.zeptomail.eu/v1.1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Zoho-enczapikey {api_key}"
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
        return response.json()

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
        return response.json()

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
