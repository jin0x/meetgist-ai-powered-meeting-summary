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

async def verify_slack_request(request: Request, x_slack_signature: str = Header(...), x_slack_timestamp: str = Header(...)) -> bool:
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

@router.post("/events")
async def slack_events(
    request: Request,
    query_service: QueryService = Depends(get_query_service)
) -> Union[Dict[str, Any], SlackResponse]:
    """Handle Slack events"""
    try:
        # Get and parse the raw body
        body = await request.body()
        body_json = await request.json()

        # Handle URL verification
        if body_json.get("type") == "url_verification":
            return SlackChallenge(
                token=body_json.get("token"),
                challenge=body_json.get("challenge"),
                type=body_json.get("type")
            ).dict()

        # For regular events, verify the request
        await verify_slack_request(request)

        # Process the event
        event_type = body_json.get("event", {}).get("type")
        if event_type == "app_mention":
            channel = body_json["event"]["channel"]
            text = body_json["event"]["text"].lower()

            if "list summaries" in text:
                summaries = await query_service.get_all_summaries()
                return format_summaries_response(summaries, channel)

        return {"status": "ok"}

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        if summary.get('created_at'):
            created_at = datetime.fromisoformat(summary['created_at']).strftime("%Y-%m-%d")
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{summary.get('transcripts', {}).get('meeting_title', 'Unknown Meeting')}*\n{created_at}"
                }
            })

    return SlackResponse(
        channel=channel,
        blocks=blocks
    )