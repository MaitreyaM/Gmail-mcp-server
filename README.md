# Gmail MCP Server

A Model Context Protocol (MCP) server for Gmail operations, deployed on Smithery.ai using Streamable HTTP transport.

## Features

- Send emails via Gmail SMTP
- Fetch recent emails from Gmail folders
- Handle email attachments
- Health check endpoint for deployment monitoring

## Deployment on Smithery.ai

This server is configured for deployment on Smithery.ai using Streamable HTTP transport.

### Configuration

The server requires the following configuration parameters:
- `smtp_username`: Your Gmail email address
- `smtp_password`: Your Gmail app password (not your regular password)

### Health Check

The server provides a health check endpoint at `/health` for Smithery deployment monitoring.


## CLAUDE CONFIG EXAMPLE 
```
{
  "mcpServers": {
    "terminal_server": {
      "command": "/Users/maitreyamishra/.local/bin/uv",
      "args": [
        "--directory", "Path to your mcp server file",
        "run",
        "terminal_server.py"
      ]
    },
    "web3_server": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:3000/mcp"
      ]
    },
    "gmail_mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8989/mcp"
      ]
    }
  }
}
```


### Port

The server runs on port 5000 and binds to all interfaces (0.0.0.0) for container deployment.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export SMTP_USERNAME="your-email@gmail.com"
   export SMTP_PASSWORD="your-app-password"
   ```

3. Run the server:
   ```bash
   python gmail_mcp.py
   ```

## Docker

Build and run with Docker:
```bash
docker build -t gmail-mcp .
docker run -p 5000:5000 -e SMTP_USERNAME=your-email -e SMTP_PASSWORD=your-password gmail-mcp
```
