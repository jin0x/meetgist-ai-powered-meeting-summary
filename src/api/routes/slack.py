from fastapi import APIRouter, HTTPException, Header, Request, Depends
from ..models.slack import (
    SlackEvent,
    SlackChallenge,
    SlackResponse
)
from ..services.query import QueryService, get_query_service
from typing import Union, Dict, Any
import hmac
import hashlib
import os
from datetime import datetime

router = APIRouter()
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

async def verify_slack_request(
    request: Request,
    x_slack_signature: str = Header(...),
    x_slack_timestamp: str = Header(...)
) -> bool:
    """Verify that the request came from Slack"""
    if not SLACK_SIGNING_SECRET:
        raise HTTPException(status_code=500, detail="Slack signing secret not configured")

    body = await request.body()
    base_string = f"v0:{x_slack_timestamp}:{body.decode()}"

    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, x_slack_signature):
        raise HTTPException(status_code=401, detail="Invalid request signature")

    return True

@router.post("/events", response_model=Union[Dict[str, str], SlackResponse])
async def slack_events(
    request: Request,
    event: Union[SlackEvent, SlackChallenge],
    query_service: QueryService = Depends(get_query_service)
) -> Union[Dict[str, str], SlackResponse]:
    """Handle Slack events"""
    # Verify request first
    await verify_slack_request(request)

    # Handle URL verification
    if hasattr(event, 'challenge'):
        return {"challenge": event.challenge}

    # Handle mention events
    if event.event.type == "app_mention":
        command_text = event.event.text.lower()

        try:
            if "list summaries" in command_text:
                summaries = await query_service.get_all_summaries()
                return format_summaries_response(summaries, event.event.channel)

        except Exception as e:
            print(f"Error processing command: {e}")
            return SlackResponse(
                channel=event.event.channel,
                text="❌ Sorry, I encountered an error processing your request."
            )

    return {"status": "ok"}

def format_summaries_response(summaries: list, channel: str) -> SlackResponse:
    """Format summaries list for Slack response"""
    if not summaries:
        return SlackResponse(
            channel=channel,
            text="No summaries found."
        )

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
        created_at = datetime.fromisoformat(summary['created_at']).strftime("%Y-%m-%-d")
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{summary['transcripts']['meeting_title']}*\n{created_at}"
            }
        })

    return SlackResponse(
        channel=channel,
        blocks=blocks
    )