# 📧 ZeptoMail Python API

[![PyPI version](https://img.shields.io/pypi/v/zeptomail-python-api.svg)](https://pypi.org/project/zeptomail-python-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/zeptomail-python-api.svg)](https://pypi.org/project/zeptomail-python-api/)
[![License](https://img.shields.io/github/license/NamiLinkLabs/zeptomail-python-api.svg)](https://github.com/NamiLinkLabs/zeptomail-python-api/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/zeptomail-python-api.svg)](https://pypi.org/project/zeptomail-python-api/)

A Python client for interacting with the ZeptoMail API.

> ⚠️ **DISCLAIMER**: This is an unofficial SDK. Namilink Kft is not affiliated with ZeptoMail or Zoho Corporation. This package is maintained independently and is not endorsed by ZeptoMail.

## ⚡ Installation

```bash
pip install zeptomail-python-api
```

Or with uv:

```bash
uv pip install zeptomail-python-api
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

### Sending Emails with Attachments

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

# Or add an attachment from a ZeptoMail file cache key
cached_attachment = client.add_attachment_from_file_cache(
    file_cache_key="your-file-cache-key",
    name="cached-document.pdf"
)

# Send email with attachments
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient],
    subject="Email with Attachments",
    html_body="<p>Please find the attached documents.</p>",
    attachments=[attachment, cached_attachment]
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

## ✨ Features

- 📨 Send single emails
- 📊 Send batch emails with personalization
- 📎 Add attachments and inline images
- 🖼️ Support for inline images with CID references
- 📈 Email tracking (opens and clicks)
- ⚙️ Customize MIME headers
- 🔍 Detailed error handling with solutions

## 🚧 Implementation Status

This library currently implements:
- ✅ Email Sending API
- ✅ Batch Email Sending API
- ✅ Attachments and Inline Images
- ✅ Personalization with merge fields

Not yet implemented:
- ❌ Templates API
- ❌ Template Management API

Contributions to implement these additional APIs are welcome!

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/NamiLinkLabs/zeptomail-python-api/issues).

## 🔒 Security

For security issues, please email security@zeptomail.eu instead of using the issue tracker.
