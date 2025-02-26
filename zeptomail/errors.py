from typing import List, Dict


class ZeptoMailError(Exception):
    """Exception raised for ZeptoMail API errors."""

    def __init__(self, message: str, code: str = None, sub_code: str = None,
                 details: List[Dict] = None, request_id: str = None):
        self.message = message
        self.code = code
        self.sub_code = sub_code
        self.details = details or []
        self.request_id = request_id

        # Build a detailed error message
        error_msg = f"ZeptoMail API Error: {message}"
        if code:
            error_msg += f" (Code: {code}"
            if sub_code:
                error_msg += f", Sub-Code: {sub_code}"
            error_msg += ")"

        if details:
            detail_messages = []
            for detail in details:
                target = detail.get("target", "")
                detail_msg = detail.get("message", "")
                if target and detail_msg:
                    detail_messages.append(f"{target}: {detail_msg}")
                elif detail_msg:
                    detail_messages.append(detail_msg)

            if detail_messages:
                error_msg += f"\nDetails: {', '.join(detail_messages)}"

        if request_id:
            error_msg += f"\nRequest ID: {request_id}"

        super().__init__(error_msg)
