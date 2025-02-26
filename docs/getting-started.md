# Getting Started

## Installation

Install the ZeptoMail Python API client using pip:

```bash
pip install zeptomail-python-api
```

## Basic Usage

Here's a simple example of how to send an email using the ZeptoMail Python API:

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

## Authentication

To use the ZeptoMail API, you need an API key. You can obtain this from your ZeptoMail account.

When initializing the client, you can provide the API key directly:

```python
client = ZeptoMail("your-api-key-here")
```

The client will automatically format the API key correctly, adding the required prefix if needed.

## Error Handling

The ZeptoMail client provides detailed error handling with helpful solutions:

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

The error messages include detailed information about what went wrong and suggestions for how to fix the issue.
