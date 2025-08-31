from mcp.server.fastmcp import FastMCP
import os
import sys
import time
import signal
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import imaplib
import email
from email.header import decode_header
from fastapi import FastAPI
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Smithery deployment"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "gmail-mcp"}
    )

SMTP_HOST = "smtp.gmail.com"    
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def signal_handler(sig, frame):
    print("Thanks for using Maitreya's server...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

mcp = FastMCP(
    name="gmail-mcp",
    host="0.0.0.0",     
    port=8989,       

)

def send_email(recipient: str, subject: str, body: str, attachment_path: str = None) -> str:
    """
    Send an email using Gmail SMTP.
    
    Parameters:
    - recipient: Email address to send to.
    - subject: Email subject.
    - body: Email body text.
    - attachment_path: Optional file path of the attachment.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            msg.attach(part)
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, recipient, msg.as_string())
        server.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"

def download_attachment_from_url(attachment_url: str, attachment_filename: str) -> str:
    """
    Download an attachment from a URL.
    
    Parameters:
    - attachment_url: URL of the attachment.
    - attachment_filename: Desired filename for the downloaded attachment.
    
    Returns:
    - The file path of the downloaded attachment.
    """
    temp_dir = "temp_attachments"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, attachment_filename)
    response = requests.get(attachment_url)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

def get_pre_staged_attachment(attachment_name: str) -> str:
    """
    Retrieve a pre-staged attachment from the local directory.
    
    Parameters:
    - attachment_name: Name of the attachment file.
    
    Returns:
    - The file path if found; otherwise, None.
    """
    attachment_dir = "available_attachments"
    file_path = os.path.join(attachment_dir, attachment_name)
    return file_path if os.path.exists(file_path) else None

@mcp.tool('send_email_tool')
def send_email_tool(recipient: str, subject: str, body: str, 
                    attachment_path: str = None, 
                    attachment_url: str = None, 
                    attachment_name: str = None) -> str:
    """
    Send an email via Gmail SMTP.
    
    Parameters:
    - recipient: The email address to send the email to.
    - subject: The email subject.
    - body: The email body text.
    - attachment_path: Optional direct file path for an attachment.
    - attachment_url: Optional URL from which to download an attachment.
    - attachment_name: Optional filename for the attachment.
    
    Priority:
      1. If attachment_url is provided (and attachment_name for filename), download the file.
      2. Else if attachment_name is provided, try to load it from the 'available_attachments' directory.
      3. Otherwise, use attachment_path if provided.
    """
    final_attachment_path = attachment_path
    if attachment_url and attachment_name:
        try:
            final_attachment_path = download_attachment_from_url(attachment_url, attachment_name)
        except Exception as e:
            return f"Failed to download attachment from URL: {e}"
    elif attachment_name:
        final_attachment_path = get_pre_staged_attachment(attachment_name)
        if not final_attachment_path:
            return f"Error: Attachment '{attachment_name}' not found in pre-staged directory."
    return send_email(recipient, subject, body, final_attachment_path)

@mcp.tool('fetch_recent_emails')
def fetch_recent_emails(folder: str = "INBOX", limit: int = 10) -> str:
    """
    Fetch the most recent emails from a specified folder.
    
    Parameters:
    - folder: The email folder to fetch from (default: "INBOX").
    - limit: Maximum number of emails to fetch (default: 10).
    
    Returns:
    - A formatted string containing details of the recent emails.
    """
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(SMTP_USERNAME, SMTP_PASSWORD)
        mail.select(folder)
        result, data = mail.search(None, "ALL")
        if not data or not data[0]:
            return "No emails found in the specified folder."
        email_ids = data[0].split()
        latest_email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
        emails = []
        for email_id in reversed(latest_email_ids):
            result, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            from_ = msg.get("From", "")
            date = msg.get("Date", "")
            emails.append({
                "id": email_id.decode(),
                "from": from_,
                "subject": subject,
                "date": date
            })
        mail.close()
        mail.logout()
        if not emails:
            return "No emails found in the specified folder."
        result_text = "Recent emails:\n\n"
        for i, email_data in enumerate(emails, 1):
            result_text += f"{i}. From: {email_data['from']}\n"
            result_text += f"   Subject: {email_data['subject']}\n"
            result_text += f"   Date: {email_data['date']}\n"
            result_text += f"   ID: {email_data['id']}\n\n"
        return result_text
    except Exception as e:
        return f"Failed to fetch emails: {e}"

if __name__ == "__main__":
    try:
        print("Starting MCP server 'gmail-mcp' on 0.0.0.0:8989")
        print("Server is ready to accept HTTP connections")
        print("Health check available at /health")
        
        # Start the MCP server
        mcp.run(transport= "streamable-http")
    except Exception as e:
        print(f"Error starting server: {e}")
        time.sleep(5)
        sys.exit(1)
