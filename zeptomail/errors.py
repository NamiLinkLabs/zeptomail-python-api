from typing import List, Dict, Optional


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
        
    @staticmethod
    def get_error_solution(code: str, sub_code: str, details: List[Dict]) -> Optional[str]:
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
                    "from": "Add the mandatory 'from' field with a valid Email address.",
                    "to": "Add at least one recipient using 'to', 'cc', or 'bcc' fields.",
                    "Mail Template Key": "Add the mandatory 'Mail Template Key' field."
                }
            },
            "TM_3301": {
                "SM_101": "Check your API request syntax for valid JSON format.",
                "SM_120": "Ensure the attachment MIME type matches the actual file content.",
                "default": "Chosen file has empty content. Fix the content to proceed."
            },
            "TM_3501": {
                "UE_106": "Use a valid File Cache Key from your Mail Agent's File Cache tab.",
                "MTR_101": "Use a valid Template Key from your Mail Agent.",
                "LE_101": "Your credits have expired. Purchase new credits from the ZeptoMail Subscription page.",
                "default": "File added violates the Secure Attachment Policy. Check ZeptoMail's secure attachment guidelines."
            },
            "TM_3601": {
                "SERR_156": "Add your sending IP to the allowed IPs list in settings.",
                "SM_133": "Your trial sending limit is exceeded. Get your account reviewed to continue.",
                "SMI_115": "Daily sending limit reached. Try again tomorrow.",
                "AE_101": "Your account is blocked. Contact ZeptoMail support."
            },
            "TM_4001": {
                "SM_111": "Use a sender email with a domain that is verified in your Mail Agent.",
                "SM_113": "Provide valid values for all required fields.",
                "SM_128": "Your account needs to be reviewed. Get your account approved before sending emails.",
                "SERR_157": "Use a valid Sendmail token from your Mail Agent configuration settings.",
                "default": "Invalid Send Mail token. Check your API key and ensure it's correctly formatted."
            },
            "TM_5001": {
                "LE_102": "Your credits are exhausted. Purchase new credits from the ZeptoMail Subscription page."
            },
            "TM_8001": {
                "SM_127": "Reduce the number of attachments to 60 or fewer.",
                "SM_129": "Ensure all name fields are under 250 characters, subject is under 500 characters, attachment size is under 15MB, and attachment filenames are under 150 characters.",
                "default": "File size exceeded. Ensure your file is under the maximum allowed size limit."
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
            
            # If no sub-code match, try to get a default solution for the main code
            elif "default" in code_solutions:
                return code_solutions["default"]
        
        return None
