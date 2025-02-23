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

    def send_meeting_summary(
        self,
        meeting_title: str,
        summary_data: Dict[str, Any],
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Send meeting summary to Slack channel.

        Args:
            meeting_title: Title of the meeting
            summary_data: Dictionary containing summary, decisions, and action items
            timestamp: Optional timestamp (defaults to current time)

        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Use current time if no timestamp provided
            if not timestamp:
                timestamp = datetime.now().isoformat()

            # Extract data from summary
            summary = summary_data.get('summary_text', 'No summary available')
            decisions = summary_data.get('key_decisions', [])
            actions = summary_data.get('action_items', [])

            # Format decisions and actions for display
            decisions_text = self._format_list(decisions, "- ")
            actions_text = self._format_list(actions, "- ")

            payload = {
                "channel": self.channel,
                "text": "*New Meeting Summary Generated*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📝 New Meeting Summary"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Meeting:*\n{meeting_title}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Generated:*\n{timestamp}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Summary*\n{summary}"
                        }
                    }
                ]
            }

            # Add decisions if available
            if decisions_text:
                payload["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Key Decisions*\n{decisions_text}"
                    }
                })

            # Add action items if available
            if actions_text:
                payload["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Action Items*\n{actions_text}"
                    }
                })

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
            print(f"Error sending Slack notification: {str(e)}")
            return False

    def _format_list(self, items: List[str], prefix: str = "- ") -> str:
        """Format a list of items for Slack display."""
        if not items:
            return "None"
        return "\n".join(f"{prefix}{item}" for item in items)