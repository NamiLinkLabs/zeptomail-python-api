# Error Handling

This page documents the error handling classes used by the ZeptoMail client.

## ZeptoMailError Class

::: zeptomail.errors.ZeptoMailError
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Common Error Codes

The ZeptoMail API returns specific error codes that can help diagnose issues:

| Error Code | Sub-Code | Description | Solution |
|------------|----------|-------------|----------|
| TM_3201 | GE_102 | Mandatory field is empty | Ensure all required fields are provided |
| TM_3301 | SM_101 | Invalid JSON format | Check your API request syntax |
| TM_3301 | SM_120 | Invalid attachment MIME type | Ensure MIME type matches file content |
| TM_3501 | UE_106 | Invalid File Cache Key | Use a valid key from your Mail Agent |
| TM_3501 | LE_101 | Credits expired | Purchase new credits |
| TM_3601 | SERR_156 | IP not allowed | Add your IP to allowed list |
| TM_3601 | SM_133 | Trial limit exceeded | Get account reviewed |
| TM_4001 | SM_111 | Unverified sender domain | Verify your domain |
| TM_5001 | LE_102 | Credits exhausted | Purchase new credits |
| TM_8001 | SM_127 | Too many attachments | Reduce to 60 or fewer |

## Example Error Handling

```python
from zeptomail import ZeptoMail, ZeptoMailError

client = ZeptoMail("your-api-key-here")

try:
    response = client.send_email(
        from_address="sender@example.com",
        from_name="Sender Name",
        to=[client.add_recipient("recipient@example.com")],
        subject="Test Email",
        html_body="<p>Test email content</p>"
    )
    print(f"Email sent successfully: {response}")
except ZeptoMailError as e:
    print(f"Error code: {e.code}")
    print(f"Error sub-code: {e.sub_code}")
    print(f"Error message: {e.message}")
    print(f"Error details: {e.details}")
    print(f"Request ID: {e.request_id}")
```
