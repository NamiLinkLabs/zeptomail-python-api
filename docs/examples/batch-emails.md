# Batch Email Examples

## Sending a Batch Email with Personalization

```python
from zeptomail import ZeptoMail

# Initialize the client
client = ZeptoMail("your-api-key-here")

# Create batch recipients with personalization data
recipients = [
    client.add_batch_recipient(
        "recipient1@example.com",
        "Recipient One",
        {"first_name": "Recipient", "last_name": "One", "order_id": "12345"}
    ),
    client.add_batch_recipient(
        "recipient2@example.com",
        "Recipient Two",
        {"first_name": "Recipient", "last_name": "Two", "order_id": "67890"}
    )
]

# Send a batch email with personalization
response = client.send_batch_email(
    from_address="sender@example.com",
    from_name="Sender Name",
    to=recipients,
    subject="Your Order {{order_id}} is Ready",
    html_body="""
    <h1>Hello {{first_name}} {{last_name}},</h1>
    <p>Your order {{order_id}} has been processed and is ready for shipping.</p>
    <p>Thank you for your business!</p>
    """,
    text_body="Hello {{first_name}} {{last_name}}, Your order {{order_id}} has been processed and is ready for shipping. Thank you for your business!",
    merge_info={"default_name": "Valued Customer"}  # Default values for recipients without specific merge info
)

print(f"Batch email sent! Response: {response}")
```

## Batch Email with Attachments and Tracking Options

```python
from zeptomail import ZeptoMail

client = ZeptoMail("your-api-key-here")

# Create batch recipients
recipients = [
    client.add_batch_recipient("user1@example.com", "User One", {"user_id": "U001"}),
    client.add_batch_recipient("user2@example.com", "User Two", {"user_id": "U002"})
]

# Create an attachment
attachment = client.add_attachment_from_content(
    content="base64encodedcontent",
    mime_type="application/pdf",
    name="report.pdf"
)

# Send batch email with attachment and custom tracking options
response = client.send_batch_email(
    from_address="reports@example.com",
    from_name="Report System",
    to=recipients,
    subject="Your Monthly Report - User {{user_id}}",
    html_body="<p>Please find your monthly report attached.</p><p>User ID: {{user_id}}</p>",
    text_body="Please find your monthly report attached. User ID: {{user_id}}",
    attachments=[attachment],
    track_clicks=True,
    track_opens=True,
    client_reference="monthly-reports-batch-{{user_id}}"
)

print(f"Batch email with attachments sent! Response: {response}")
```
