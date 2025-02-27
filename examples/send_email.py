import os

from dotenv import load_dotenv

from zeptomail import ZeptoMail
env = load_dotenv()
def main():
    # Replace with your actual API key
    api_key = os.getenv('API_KEY')
    
    # Initialize the client
    client = ZeptoMail(api_key)
    
    # Create a recipient
    recipient = client.add_recipient(os.getenv('TEST_EMAIL'), "Recipient Name")
    
    # Send a simple email
    response = client.send_email(
        from_address=os.getenv('SENDER_EMAIL'),
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
