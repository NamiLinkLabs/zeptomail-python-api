# Working with Attachments

This guide shows how to work with attachments and inline images in the ZeptoMail API.

## Adding File Attachments

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Method 1: Add attachment from base64 encoded content
attachment1 = client.add_attachment_from_content(
    content="base64encodedcontent",  # Base64 encoded file content
    mime_type="application/pdf",
    name="report.pdf"
)

# Method 2: Add attachment from ZeptoMail file cache
attachment2 = client.add_attachment_from_file_cache(
    file_cache_key="file-cache-key-123",
    name="cached-document.pdf"
)

# Send email with multiple attachments
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Attachments",
    html_body="<p>Please find the attached documents.</p>",
    text_body="Please find the attached documents.",
    attachments=[attachment1, attachment2]
)

print(f"Response: {response}")
```

## Working with Inline Images

Inline images are embedded directly in the HTML content of your email:

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Create an inline image with base64 encoded content
inline_image = client.add_inline_image(
    cid="logo123",  # Content ID to reference in HTML
    content="base64encodedimage",  # Base64 encoded image content
    mime_type="image/png"
)

# Alternative: Create an inline image from file cache
# inline_image = client.add_inline_image(
#     cid="logo123",
#     file_cache_key="file-cache-key-456"
# )

# Send email with inline image
# Note: The image is referenced in HTML using the cid
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[client.add_recipient("recipient@example.com", "Recipient Name")],
    subject="Email with Inline Image",
    html_body="""
    <p>Here's our company logo:</p>
    <img src="cid:logo123" alt="Company Logo" width="200">
    <p>Best regards,<br>The Team</p>
    """,
    text_body="Please view this email in an HTML-compatible email client to see our logo.",
    inline_images=[inline_image]
)

print(f"Response: {response}")
```

## Size Limitations

When working with attachments, keep in mind:

- Maximum attachment size: 15MB per attachment
- Maximum total email size: 25MB
- Maximum number of attachments: 60 per email
- Maximum attachment filename length: 150 characters

If you need to send larger files, consider using a file sharing service and including the download link in your email.
