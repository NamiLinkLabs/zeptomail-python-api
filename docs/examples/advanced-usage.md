# Advanced Usage

This page covers advanced usage scenarios for the ZeptoMail Python API.

## Custom MIME Headers

You can add custom MIME headers to your emails:

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Define custom MIME headers
mime_headers = {
    "X-Custom-ID": "campaign-123",
    "X-Priority": "1",
    "X-Campaign-Source": "newsletter"
}

# Send email with custom headers
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Custom Headers",
    html_body="<p>This email has custom MIME headers.</p>",
    mime_headers=mime_headers
)

print(f"Response: {response}")
```

## Tracking Options

Control click and open tracking:

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Send email with tracking options
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Tracking Options",
    html_body="<p>This email has custom tracking settings.</p>",
    track_opens=True,   # Track when recipients open the email
    track_clicks=False  # Don't track link clicks
)

print(f"Response: {response}")
```

## Client Reference

The `client_reference` parameter allows you to add your own identifier to emails:

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Send email with client reference
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Client Reference",
    html_body="<p>This email has a client reference.</p>",
    client_reference="order-confirmation-12345"  # Your custom reference
)

print(f"Response: {response}")
```

## Error Handling with Solutions

The ZeptoMail client provides detailed error handling with suggested solutions:

```python
from zeptomail import ZeptoMail, ZeptoMailError

client = ZeptoMail("your-api-key-here")

try:
    response = client.send_email(
        from_address="sender@example.com",
        from_name="Sender Name",
        to=[client.add_recipient("recipient@example.com")],
        subject="",  # Empty subject will cause an error
        html_body="<p>Test email content</p>"
    )
    print(f"Email sent successfully: {response}")
except ZeptoMailError as e:
    print(f"Error sending email: {e}")
    # Output will include the error and a suggested solution:
    # ZeptoMail API Error: Mandatory Field 'subject' was set as Empty Value. 
    # (Code: TM_3201, Sub-Code: GE_102)
    # Details: subject: This field is required
    # Set a non-empty subject for your email.
```

## Working with Bytes Objects

The client automatically handles conversion of bytes to base64:

```python
from zeptomail import ZeptoMail
import base64

client = ZeptoMail("your-api-key-here")

# Read a file as bytes
with open("document.pdf", "rb") as f:
    file_bytes = f.read()

# The client will automatically convert bytes to base64
attachment = client.add_attachment_from_content(
    content=file_bytes,  # Can be bytes or base64 string
    mime_type="application/pdf",
    name="document.pdf"
)

response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Attachment",
    html_body="<p>Please find the attached document.</p>",
    attachments=[attachment]
)

print(f"Response: {response}")
```
