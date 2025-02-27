from zeptomail import ZeptoMail

def main():
    # Replace with your actual API key
    api_key = "your-api-key-here"
    
    # Initialize the client
    client = ZeptoMail(api_key)
    
    # Create a recipient
    recipient = client.add_recipient("recipient@example.com", "Recipient Name")
    
    # Send a simple email
    response = client.send_email(
        from_email="sender@example.com",
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
