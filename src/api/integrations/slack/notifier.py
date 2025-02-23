from typing import List, Optional, Dict, Any
import os
import requests
from datetime import datetime

class SlackNotifier:
    def __init__(self, token: str = None, channel: str = None):
        """Initialize Slack notifier with credentials."""
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = channel or os.getenv("SLACK_CHANNEL_ID")

        if not self.token or not self.channel:
            raise ValueError("Slack credentials not properly configured")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://slack.com/api/chat.postMessage"

        # Define colors for different sections
        self.colors = {
            "title": "#36a64f",      # Green
            "timestamp": "#ffcc00",   # Yellow
            "summary": "#ff5733",     # Orange/Red
            "decisions": "#0088cc",   # Blue
            "actions": "#800080"      # Purple
        }

    def send_meeting_summary(
        self,
        meeting_title: str,
        summary_data: Dict[str, Any],
        timestamp: Optional[str] = None,
        channel: Optional[str] = None
    ) -> bool:
        """Send meeting summary to Slack channel with enhanced formatting."""
        try:
            if not timestamp:
                timestamp = datetime.now().isoformat()

            summary = summary_data.get('summary_text', 'No summary available')
            decisions = summary_data.get('key_decisions', [])
            actions = summary_data.get('action_items', [])

            # Create the message payload
            payload = {
                "channel": channel or self.channel,
                "text": "📝 *New Meeting Summary*",
                "attachments": [
                    # Meeting Title (Green)
                    {
                        "color": self.colors["title"],
                        "fields": [{
                            "title": "Meeting Title",
                            "value": meeting_title,
                            "short": True
                        }]
                    },
                    # Timestamp (Yellow)
                    {
                        "color": self.colors["timestamp"],
                        "fields": [{
                            "title": "Generated At",
                            "value": timestamp,
                            "short": True
                        }]
                    },
                    # Summary (Orange/Red)
                    {
                        "color": self.colors["summary"],
                        "fields": [{
                            "title": "Summary",
                            "value": summary,
                            "short": False
                        }]
                    }
                ]
            }

            # Add colored decisions section if available
            if decisions:
                payload["attachments"].append({
                    "color": self.colors["decisions"],
                    "fields": [{
                        "title": "Key Decisions",
                        "value": self._format_list(decisions),
                        "short": False
                    }]
                })

            # Add colored actions section if available
            if actions:
                payload["attachments"].append({
                    "color": self.colors["actions"],
                    "fields": [{
                        "title": "Action Items",
                        "value": self._format_list(actions),
                        "short": False
                    }]
                })

            return self._send_message(payload)

        except Exception as e:
            print(f"Error sending meeting summary: {str(e)}")
            return False

    def send_summaries_list(
        self,
        summaries: List[Dict[str, Any]],
        channel: Optional[str] = None
    ) -> bool:
        """Send formatted list of available summaries."""
        try:
            if not summaries:
                return self._send_message({
                    "channel": channel or self.channel,
                    "text": "No summaries found."
                })

            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Available Summaries",
                        "emoji": True
                    }
                }
            ]

            for summary in summaries:
                if summary.get('created_at'):
                    created_at = datetime.fromisoformat(summary['created_at']).strftime("%Y-%m-%d")
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{summary.get('transcripts', {}).get('meeting_title', 'Unknown Meeting')}*\n{created_at}"
                        }
                    })

            return self._send_message({
                "channel": channel or self.channel,
                "blocks": blocks
            })

        except Exception as e:
            print(f"Error sending summaries list: {str(e)}")
            return False

    def _send_message(self, payload: Dict[str, Any]) -> bool:
        """Send message to Slack."""
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )

            if not response.ok:
                print(f"Slack API Error: {response.status_code} - {response.text}")
                return False

            result = response.json()
            if not result.get("ok"):
                print(f"Slack API Error: {result.get('error', 'Unknown error')}")
                return False

            return True

        except Exception as e:
            print(f"Error sending message to Slack: {str(e)}")
            return False

    def _format_list(self, items: List[str], prefix: str = "• ") -> str:
        """Format a list of items for Slack display."""
        if not items:
            return "None"
        return "\n".join(f"{prefix}{item}" for item in items)