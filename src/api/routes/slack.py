from fastapi import APIRouter, HTTPException, Header, Request, Depends
from ..models.slack import SlackChallenge, SlackEvent, SlackResponse
from ..services.query import QueryService, get_query_service
from typing import Union, Dict, Any
import hmac
import hashlib
import os
from datetime import datetime

router = APIRouter()
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

@router.post("/events")
async def slack_events(
    request: Request,
) -> Dict[str, Any]:
    """Handle Slack events"""
    try:
        # Get the raw body first
        body = await request.body()
        body_text = body.decode()
        print(f"Received body: {body_text}")  # Debug print

        # Parse the body
        body_json = await request.json()
        print(f"Parsed JSON: {body_json}")  # Debug print

        # Handle URL verification
        if body_json.get("type") == "url_verification":
            challenge = body_json.get("challenge")
            print(f"Returning challenge: {challenge}")  # Debug print
            return {"challenge": challenge}

        # For other events, proceed with normal handling
        event_type = body_json.get("event", {}).get("type")
        if event_type == "app_mention":
            channel = body_json["event"]["channel"]
            text = body_json["event"]["text"]

            if "list summaries" in text.lower():
                # Get query service
                query_service = get_query_service()
                summaries = await query_service.get_all_summaries()
                return format_summaries_response(summaries, channel)

        return {"status": "ok"}

    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))

def format_summaries_response(summaries: list, channel: str) -> Dict[str, Any]:
    """Format summaries list for Slack response"""
    if not summaries:
        return {
            "channel": channel,
            "text": "No summaries found."
        }

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

    return {
        "channel": channel,
        "blocks": blocks
    }