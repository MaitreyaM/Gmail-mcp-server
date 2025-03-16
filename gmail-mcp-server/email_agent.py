import os
import json
import requests
from datetime import datetime
from supabase import create_client, Client
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv(override=True)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Gmail SMTP Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Fetch data from Supabase tables
def fetch_data_from_supabase():
    try:
        eco_info_response = supabase.table("eco_info").select("*").order("timestamp", desc=True).limit(1).execute()
        eco_info_data = eco_info_response.data[0] if eco_info_response.data else None

        btc_price_response = supabase.table("btc_price").select("*").order("timestamp", desc=True).limit(10).execute()
        btc_price_data = btc_price_response.data if btc_price_response.data else None

        return eco_info_data, btc_price_data
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return None, None


def generate_analysis(eco_info, btc_price_data):
    try:
        # Extract the latest Bitcoin price entry for context
        latest_btc_price = btc_price_data[0] if btc_price_data else None
        if not latest_btc_price:
            raise ValueError("No Bitcoin price data available for analysis.")

        # Prepare context for the AI model
        context = (
            f"Latest Financial News: {eco_info['finance_info']}\n\n"
            f"Latest Bitcoin Price: ₹{latest_btc_price['price']} at {latest_btc_price['timestamp']}\n\n"
            "Provide a short, professional analysis of the above data:"
        )

        # Define the AI agent
        agent = Agent(
            model=Groq(id="llama-3.1-70b-versatile"),
            show_tool_calls=True,
            markdown=True,
            instructions=["Write a concise professional analysis based on the given context."],
            debug_mode=True,
        )

        # Run the agent with the context
        response = agent.run(context)

        # Debugging: Print the raw response
        print("Raw AI Response (type):", type(response))
        print("Raw AI Response (content):", response)

        # Extract the content attribute from the RunResponse object
        if hasattr(response, "content"):
            analysis = response.content.strip()
            print(f"Generated Analysis: {analysis}")
            return analysis

        # Fallback if no analysis can be extracted
        print("Failed to extract analysis. Returning default message.")
        return "Unable to generate analysis at this time."
    except Exception as e:
        # Catch and log errors
        print(f"Error during AI analysis generation: {e}")
        return "Error generating analysis."






# Generate graph and save it as an image
def generate_btc_graph(btc_price_data):
    try:
        timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in btc_price_data]
        prices = [entry["price"] for entry in btc_price_data]

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, prices, marker="o", color="blue", label="BTC Price (INR)")
        plt.title("Bitcoin (BTC) Price Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Price (INR)")
        plt.grid()
        plt.legend()
        graph_path = "btc_price_graph.png"
        plt.savefig(graph_path)
        plt.close()
        print(f"Graph saved as {graph_path}")
        return graph_path
    except Exception as e:
        print(f"Error generating graph: {e}")
        return None


# Send email with analysis and graph attachment
def send_email_with_attachment(subject, body, attachment_path):
    try:
        recipient = SMTP_USERNAME  # Sending to yourself
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject

        # Attach email body
        msg.attach(MIMEText(body, "plain"))

        # Attach the graph
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(attachment_path)}",
            )
            msg.attach(part)

        # Connect to SMTP server and send email
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, recipient, msg.as_string())
        print(f"Email sent successfully to {recipient}")
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


# Main function
def run_email_agent():
    print("Running finance_email_agent...")

    # Fetch data from Supabase
    eco_info, btc_price_data = fetch_data_from_supabase()
    if not eco_info or not btc_price_data:
        print("No data available for analysis.")
        return

    # Generate financial analysis
    analysis = generate_analysis(eco_info, btc_price_data)

    # Generate graph
    graph_path = generate_btc_graph(btc_price_data)

    # Send email
    email_body = f"{analysis}\n\nAttached is the graph showing Bitcoin price trends."
    send_email_with_attachment(
        subject="Latest Financial Analysis with BTC Price Graph",
        body=email_body,
        attachment_path=graph_path,
    )


# Execute the email agent
if __name__ == "__main__":
    run_email_agent()
