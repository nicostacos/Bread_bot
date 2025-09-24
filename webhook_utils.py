import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_webhook_message(content: str):
    """Send a plain message to Discord via webhook"""
    if not WEBHOOK_URL:
        raise ValueError("No webhook URL found in .env")

    payload = {"content": content}
    response = requests.post(WEBHOOK_URL, json=payload)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Webhook failed: {e} - {response.text}")
