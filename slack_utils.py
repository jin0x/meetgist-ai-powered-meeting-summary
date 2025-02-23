import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Slack Token & Channel
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL_ID")  # Replace with your actual channel ID

def send_slack_notification(meeting_title, summary, decisions, action_items, timestamp="2025-02-18T14:00:00Z"):
    """
    Sends a meeting summary to Slack with details.

    Args:
        meeting_title (str): Title of the meeting.
        summary (str): Summary of the meeting.
        decisions (list): List of key decisions.
        action_items (list): List of action items.
        timestamp (str): Meeting timestamp.
    """

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "channel": SLACK_CHANNEL,
        "text": "*Meeting Summary Generated*",
        "attachments": [
            {
                "color": "#36a64f",
                "fields": [{"title": "Meeting Title", "value": meeting_title, "short": True}]
            },
            {
                "color": "#ffcc00",
                "fields": [{"title": "Generated At", "value": timestamp, "short": True}]
            },
            {
                "color": "#ff5733",
                "fields": [{"title": "Summary", "value": summary, "short": False}]
            },
            {
                "color": "#0088cc",
                "fields": [{"title": "Key Decisions", "value": "\n".join(decisions), "short": False}]
            },
            {
                "color": "#800080",
                "fields": [{"title": "Action Items", "value": "\n".join(action_items), "short": False}]
            }
        ]
    }

    response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, data=json.dumps(payload))

    if response.status_code == 200 and response.json().get("ok"):
        return True
    else:
        print("Slack API Error:", response.json())
        return False
