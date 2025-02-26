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

## 🚀 Quick Start

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

## ✨ Features

- 📨 Send single emails
- 📊 Send batch emails with personalization
- 📎 Add attachments and inline images
- ⚙️ Customize MIME headers
- 🔍 Detailed error handling with solutions

## 📚 Documentation

For detailed documentation, check out:

- [Getting Started](getting-started.md)
- [API Reference](api/client.md)
- [Examples](examples/basic-usage.md)
