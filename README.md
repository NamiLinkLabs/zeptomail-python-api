# 📧 ZeptoMail Python API

[![PyPI version](https://img.shields.io/pypi/v/zeptomail-python-api.svg)](https://pypi.org/project/zeptomail-python-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/zeptomail-python-api.svg)](https://pypi.org/project/zeptomail-python-api/)
[![License](https://img.shields.io/github/license/NamiLinkLabs/zeptomail-python-api.svg)](https://github.com/NamiLinkLabs/zeptomail-python-api/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/zeptomail-python-api.svg)](https://pypi.org/project/zeptomail-python-api/)

A Python client for interacting with the ZeptoMail API.

> ⚠️ **DISCLAIMER**: This is an unofficial SDK. Namilink Kft is not affiliated with ZeptoMail or Zoho Corporation. This package is maintained independently and is not endorsed by ZeptoMail.

## ⚡ Installation

### Core Client Only
For just the email client functionality (no webhook support):

```bash
pip install zeptomail-python-api
```

### With Webhook Support
For full functionality including webhook handling:

```bash
pip install zeptomail-python-api[webhooks]
```

Or with uv:

```bash
# Core client only
uv pip install zeptomail-python-api

# With webhook support
uv pip install "zeptomail-python-api[webhooks]"
```

## 🚀 Usage

### Basic Email Sending

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

### Using File Cache for Attachments

ZeptoMail's file cache allows you to upload files once and reuse them across multiple emails, improving performance for large files or batch operations.

```python
# Upload a file to ZeptoMail's file cache
with open("document.pdf", "rb") as f:
    file_data = f.read()

upload_response = client.upload_file(
    file_data=file_data,
    file_name="document.pdf",
    content_type="application/pdf"
)

file_cache_key = upload_response.get('file_cache_key')

# Create attachment using the file cache key
attachment = client.add_attachment_from_file_cache(
    file_cache_key=file_cache_key,
    name="document.pdf"
)

# Send email with cached attachment
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient],
    subject="Email with Cached Attachment",
    html_body="<p>Please find the attached document.</p>",
    attachments=[attachment]
)
```

### Traditional Attachments (Base64)

You can also send attachments using base64-encoded content:

```python
import base64

# Add an attachment from file content
with open("document.pdf", "rb") as f:
    file_content = base64.b64encode(f.read()).decode('utf-8')

attachment = client.add_attachment_from_content(
    content=file_content,
    mime_type="application/pdf",
    name="document.pdf"
)

# Send email with attachment
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient],
    subject="Email with Base64 Attachment",
    html_body="<p>Please find the attached document.</p>",
    attachments=[attachment]
)
```

### Sending Batch Emails with Personalization

```python
# Create batch recipients with personalization
recipient1 = client.add_batch_recipient(
    email="user1@example.com",
    name="User One",
    merge_info={"first_name": "User", "last_name": "One", "id": "12345"}
)

recipient2 = client.add_batch_recipient(
    email="user2@example.com",
    name="User Two",
    merge_info={"first_name": "User", "last_name": "Two", "id": "67890"}
)

# Send batch email with personalization
response = client.send_batch_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient1, recipient2],
    subject="Hello {{first_name}}!",
    html_body="<p>Hi {{first_name}} {{last_name}},</p><p>Your ID is: {{id}}</p>",
    text_body="Hi {{first_name}} {{last_name}}, Your ID is: {{id}}",
)
```

### Adding Inline Images

```python
# Add an inline image
with open("logo.png", "rb") as f:
    image_content = base64.b64encode(f.read()).decode('utf-8')

inline_image = client.add_inline_image(
    cid="logo",  # This will be referenced in the HTML as <img src="cid:logo">
    content=image_content,
    mime_type="image/png"
)

# Send email with inline image
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient],
    subject="Email with Inline Image",
    html_body='<p>Here is our logo:</p><img src="cid:logo" alt="Logo">',
    inline_images=[inline_image]
)
```

### Webhook Handling (Optional)

If you installed with webhook support, you can handle ZeptoMail webhook events:

```python
from zeptomail.webhooks import webhook_router, register_mailagent_key, register_handler
from zeptomail.webhooks import BounceEvent, OpenEvent, ClickEvent
from fastapi import FastAPI

app = FastAPI()

# Register your mailagent key for webhook validation
register_mailagent_key("your-mailagent-key")

# Register event handlers
@register_handler("hardbounce")
def handle_bounce(event: BounceEvent):
    print(f"Email bounced: {event.data.email_info.to}")

@register_handler("email_open")
def handle_open(event: OpenEvent):
    print(f"Email opened: {event.data.email_info.to}")

@register_handler("email_link_click")
def handle_click(event: ClickEvent):
    print(f"Link clicked: {event.data.click_details.url}")

# Include the webhook router
app.include_router(webhook_router)
```

## ✨ Features

- 📨 Send single emails
- 📊 Send batch emails with personalization
- 📎 File cache for efficient attachment handling
- 📎 Traditional base64 attachments
- 🖼️ Support for inline images with CID references
- 📈 Email tracking (opens and clicks)
- ⚙️ Customize MIME headers
- 🔍 Detailed error handling with solutions
- 🪝 Webhook event handling (optional dependency)

## 🚧 Implementation Status

This library currently implements:
- ✅ Email Sending API
- ✅ Batch Email Sending API
- ✅ File Cache API for efficient attachment handling
- ✅ Traditional base64 attachments and inline images
- ✅ Personalization with merge fields
- ✅ Webhook event handling (optional FastAPI dependency)
- ✅ Modular architecture with optional dependencies

Not yet implemented:
- ❌ Templates API
- ❌ Template Management API

Contributions to implement these additional APIs are welcome!

## 📦 Dependencies

### Core Dependencies
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management

### Optional Dependencies (webhooks)
- `fastapi` - Web framework for webhook handling
- `pydantic` - Data validation for webhook events
- `uvicorn` - ASGI server for running webhook endpoints

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/NamiLinkLabs/zeptomail-python-api/issues).

## 🔒 Security

For security issues, please email security@zeptomail.eu instead of using the issue tracker.
