# Basic Usage Examples

## Sending a Simple Email

```python
from zeptomail import ZeptoMail

# Initialize the client
client = ZeptoMail("your-api-key-here")

# Create a recipient
recipient = client.add_recipient("recipient@example.com", "Recipient Name")

# Send a simple email
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient],
    subject="Test Email from ZeptoMail Python API",
    html_body="<h1>Hello World!</h1><p>This is a test email sent using the ZeptoMail Python API.</p>",
    text_body="Hello World! This is a test email sent using the ZeptoMail Python API."
)

print(f"Response: {response}")
```

## Adding Attachments

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Create an attachment from content
attachment = client.add_attachment_from_content(
    content="base64encodedcontent",  # Base64 encoded file content
    mime_type="application/pdf",
    name="document.pdf"
)

# Or create an attachment from a file cache key
# attachment = client.add_attachment_from_file_cache(
#     file_cache_key="file-cache-key-123",
#     name="document.pdf"
# )

# Send email with attachment
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

## Adding Inline Images

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Create an inline image
inline_image = client.add_inline_image(
    cid="image123",  # Content ID to reference in HTML
    content="base64encodedimage",  # Base64 encoded image content
    mime_type="image/jpeg"
)

# Send email with inline image
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Inline Image",
    html_body="<p>Here's an inline image:</p><img src='cid:image123' alt='Inline Image'>",
    inline_images=[inline_image]
)

print(f"Response: {response}")
```

## Error Handling

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
    print(f"Error sending email: {e}")
```
