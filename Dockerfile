FROM python:3.10-alpine

WORKDIR /app

# Copy entire repository into container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r gmail-mcp-server/requirements.txt

# Expose the MCP server port
EXPOSE 8989

# Start the MCP server
CMD ["python", "gmail-mcp-server/gmail_mcp.py"]
