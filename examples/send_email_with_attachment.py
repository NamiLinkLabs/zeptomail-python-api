import os
import base64

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
    
    # Create a text file to attach
    sample_text = "This is a sample text file that will be attached to the email.\n"
    sample_text += "It demonstrates how to send attachments with ZeptoMail.\n"
    
    # Create a temporary text file
    with open("sample_attachment.txt", "w") as f:
        f.write(sample_text)
    
    # Read the file and encode it as base64
    with open("sample_attachment.txt", "rb") as f:
        file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    # Create an attachment using the encoded content
    attachment = client.add_attachment_from_content(
        content=encoded_content,
        mime_type="text/plain",
        name="sample_document.txt"
    )
    
    # Send an email with the attachment
    response = client.send_email(
        from_address=os.getenv("SENDER_EMAIL"),
        from_name="Sender Name",
        to=[recipient],
        subject="Email with Text Attachment",
        html_body="<h1>Email with Attachment</h1><p>This email contains a text file attachment.</p>",
        text_body="Email with Attachment\n\nThis email contains a text file attachment.",
        attachments=[attachment]
    )
    
    print("Email with attachment sent!")
    print(f"Response: {response}")
    
    # Clean up the temporary file
    os.remove("sample_attachment.txt")
    print("Temporary file removed.")

if __name__ == "__main__":
    main()
