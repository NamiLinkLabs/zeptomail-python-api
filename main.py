from zeptomail import ZeptoMail

def main():
    # Example usage of the ZeptoMail client
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
    
    print("Email sent!")
    print(f"Response: {response}")

if __name__ == "__main__":
    main()
