# Gmail-mcp-server
A resilient MCP server built with fastMCP for sending emails through Gmail's SMTP server using AI agents.
[![smithery badge](https://smithery.ai/badge/@MaitreyaM/gmail-mcp-server)](https://smithery.ai/server/@MaitreyaM/gmail-mcp-server)

# Gmail MCP Server

This repository contains a resilient MCP server implementation using [fastMCP](https://github.com/your-link-to-fastMCP). The server is designed to send emails via Gmail's SMTP server and supports various methods for attaching files, including:

- **Direct File Path:** Attach files that exist on the local filesystem.
- **URL-Based Attachments:** Download files from a given URL and attach them.
- **Pre-Staged Attachments:** Use attachments stored in a designated directory.

The server is built with resilience in mind, featuring an increased timeout and graceful shutdown handling.

## Features

- **Gmail SMTP Integration:** Sends emails using Gmail’s SMTP server with TLS. ( MAKE SURE YOU HAVE SETUP GMAIL SMTP ON YOUR ACCOUNT AND GENERATE APP password )
- **Multiple Attachment Methods:** 
  - Directly from a file path.
  - By downloading from a public URL.
  - Using pre-staged attachments stored locally.
- **Resilient Design:** Increased timeout and signal handling for graceful shutdown.
- **Environment-Based Configuration:** Securely manage your Gmail credentials using environment variables.

## Requirements

- Python 3.x
- [fastMCP](https://pypi.org/project/mcp/) (install via `pip install mcp`)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (install via `pip install python-dotenv`)
- [requests](https://pypi.org/project/requests/) (install via `pip install requests`)

## Setup

1. **Clone the Repository:**

   ```bash
   git clone <remote-repository-URL>
   cd gmail-mcp-server


Set Up Environment Variables:

Create a `.env` file in the root directory and add your Gmail SMTP credentials:

SMTP_USERNAME=your.email@gmail.com 
SMTP_PASSWORD=your_app_password


Note: If you use 2-Step Verification on your Gmail account, you must generate and use an App Password.

OPEN CLAUDE > SETTINGS > MCP > Configure > OPEN claude_desktop_config.json > Paste the file with your path below
{
  "mcpServers": {
    "gmail-mcp": {
      "command": "python",
      "args": ["PATH_TO_gmail_mcp.py"],
      "host": "127.0.0.1",
      "port": 5000,
      "timeout": 30000
    }
  }
}

(Optional) Prepare Attachment Directories:

For pre-staged attachments, create a directory named `available_attachments` in the root.
The server will automatically create a `temp_attachments` directory when downloading files from URLs.

Running the Server:
To start the MCP server, run:

```bash
python server.py

The server will start on 127.0.0.1:5000 and can be accessed by your MCP clients or agents.

Usage
Sending Emails

You can send emails using the send_email_tool with the following parameters:

recipient: Email address of the recipient.
subject: Email subject.
body: Email body text.
attachment_path (optional): Direct file path to the attachment.
attachment_url (optional): Public URL from which to download the attachment.
attachment_name (optional): Filename to use for the attachment (required when using URL-based or pre-staged attachments).
Example Scenarios:

Direct File Attachment:

json
Copy
{
  "recipient": "friend@example.com",
  "subject": "Hello with attachment",
  "body": "Please see the attached document.",
  "attachment_path": "C:\\path\\to\\document.pdf"
}

URL-Based Attachment:

json
Copy
{
  "recipient": "friend@example.com",
  "subject": "Hello with attachment",
  "body": "Please see the attached image.",
  "attachment_url": "https://example.com/image.png",
  "attachment_name": "image.png"
}
Pre-Staged Attachment:

Place your file in the available_attachments directory and reference it by name:

json
Copy
{
  "recipient": "friend@example.com",
  "subject": "Hello with attachment",
  "body": "Please see the attached file.",
  "attachment_name": "document.pdf"
}
License:
This project is licensed under the MIT License.

Contributing:
Contributions are welcome! Feel free to open issues or submit pull requests.

Acknowledgments:
Built with fastMCP.
Inspired by resilient design patterns for server applications.
