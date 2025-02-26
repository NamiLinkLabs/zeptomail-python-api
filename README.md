# ZeptoMail Python API

A Python client for interacting with the ZeptoMail API.

## Installation

```bash
pip install zeptomail-python-api
```

Or with uv:

```bash
uv pip install zeptomail-python-api
```

## Usage

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

## Features

- Send single emails
- Send batch emails with personalization
- Add attachments and inline images
- Customize MIME headers

## License

MIT License - see the [LICENSE](LICENSE) file for details.
