import os
import tempfile

from dotenv import load_dotenv

from zeptomail import ZeptoMail

env = load_dotenv()

def main():
    # Replace with your actual API key
    api_key = os.getenv('API_KEY')
    
    # Initialize the client
    client = ZeptoMail(api_key)
    
    # Create a temporary file to demonstrate file upload
    sample_content = "This is a sample file content for testing file cache functionality."
    
    # Method 1: Upload file using file_data (bytes)
    print("Uploading file using file_data...")
    file_data = sample_content.encode('utf-8')
    upload_response = client.upload_file(
        file_data=file_data,
        file_name="sample_document.txt",
        content_type="text/plain"
    )
    
    print(f"File uploaded successfully!")
    print(f"File cache key: {upload_response.get('file_cache_key')}")
    file_cache_key = upload_response.get('file_cache_key')

    
    # Create a recipient
    recipient = client.add_recipient(os.getenv('TEST_EMAIL'), "Recipient Name")
    
    # Create attachment using the file cache key
    attachment = client.add_attachment_from_file_cache(
        file_cache_key=file_cache_key,
        name="sample_document.txt"
    )
    
    # Send email with the cached file as attachment
    print("Sending email with cached file attachment...")
    response = client.send_email(
        from_address=os.getenv('SENDER_EMAIL'),
        from_name="Sender Name",
        to=[recipient],
        subject="Test Email with File Cache Attachment",
        html_body="""
        <h1>File Cache Example</h1>
        <p>This email demonstrates how to use ZeptoMail's file cache functionality.</p>
        <p>The attached file was first uploaded to ZeptoMail's file cache, then referenced in this email.</p>
        <p>Benefits of using file cache:</p>
        <ul>
            <li>Faster email sending for large files</li>
            <li>Ability to reuse files across multiple emails</li>
            <li>Better performance for batch emails with same attachments</li>
        </ul>
        """,
        text_body="""
        File Cache Example
        
        This email demonstrates how to use ZeptoMail's file cache functionality.
        
        The attached file was first uploaded to ZeptoMail's file cache, then referenced in this email.
        
        Benefits of using file cache:
        - Faster email sending for large files
        - Ability to reuse files across multiple emails  
        - Better performance for batch emails with same attachments
        """,
        attachments=[attachment]
    )
    
    print("Email sent successfully!")
    print(f"Response: {response}")
    
    # Example: Reusing the same file cache key for another email
    print("\nSending second email with the same cached file...")
    second_response = client.send_email(
        from_address=os.getenv('SENDER_EMAIL'),
        from_name="Sender Name",
        to=[recipient],
        subject="Second Email - Reusing Cached File",
        html_body="<p>This email reuses the same file from cache, demonstrating efficiency!</p>",
        text_body="This email reuses the same file from cache, demonstrating efficiency!",
        attachments=[attachment]
    )
    
    print("Second email sent successfully!")
    print(f"Response: {second_response}")

if __name__ == "__main__":
    main()
