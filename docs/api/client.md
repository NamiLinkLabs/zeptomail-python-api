# ZeptoMail Client

This page documents the main `ZeptoMail` client class and its methods.

## Class Reference

::: zeptomail.client.ZeptoMail
    options:
      show_source: true
      show_if_no_docstring: true
      heading_level: 3

!!! note "Source Code in LLMs"
    When generating the LLMs text file, only function signatures and docstrings are included, not the implementation details.

## Usage Examples

### Basic Initialization

```python
from zeptomail import ZeptoMail

# Initialize with API key
client = ZeptoMail("your-api-key-here")

# Or with custom base URL (for different regions)
client = ZeptoMail(
    api_key="your-api-key-here",
    base_url="https://api.zeptomail.com/v1.1"  # Custom API endpoint
)
```

### Sending a Simple Email

```python
# Create a recipient
recipient = client.add_recipient("recipient@example.com", "Recipient Name")

# Send a simple email
response = client.send_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=[recipient],
    subject="Test Email",
    html_body="<h1>Hello World!</h1><p>This is a test email.</p>",
    text_body="Hello World! This is a test email."
)

print(f"Email sent with message ID: {response['data']['message_id']}")
```

See the [Examples](../examples/basic-usage.md) section for more detailed usage examples.
