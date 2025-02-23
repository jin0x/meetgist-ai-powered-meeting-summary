from fastapi import APIRouter, HTTPException, Header, Request, Depends
from ..models.slack import SlackChallenge, SlackEvent, SlackResponse
from ..services.query import QueryService, get_query_service
from typing import Union, Dict, Any
import hmac
import hashlib
import os
from datetime import datetime
import json

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

@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    print("Test endpoint hit!")  # Debug log
    return {"message": "Test endpoint working"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    print("Health check endpoint hit!")  # Debug log
    return {"status": "healthy"}

@router.post("/events")
async def slack_events(
    request: Request,
    query_service: QueryService = Depends(get_query_service)
) -> Union[Dict[str, Any], SlackResponse]:
    """Handle Slack events"""
    try:
        # Get and parse the raw body
        body = await request.body()
        body_text = body.decode()
        print(f"Received raw body: {body_text}")  # Debug log

        body_json = await request.json()
        print(f"Parsed JSON: {json.dumps(body_json, indent=2)}")  # Debug log

        # Handle URL verification
        if body_json.get("type") == "url_verification":
            print("Handling URL verification")  # Debug log
            return SlackChallenge(
                token=body_json.get("token"),
                challenge=body_json.get("challenge"),
                type=body_json.get("type")
            ).dict()

        # For regular events, verify the request
        await verify_slack_request(request)

        # Parse the event using our model
        try:
            event = SlackEvent(**body_json)
            print(f"Parsed Slack event: {event}")  # Debug log
        except Exception as e:
            print(f"Error parsing event: {e}")  # Debug log
            event = body_json  # Fallback to raw JSON

        # Process the event
        event_type = body_json.get("event", {}).get("type")
        print(f"Event type: {event_type}")  # Debug log

        if event_type == "app_mention":
            channel = body_json["event"]["channel"]
            text = body_json["event"]["text"].lower()
            print(f"Received command in channel {channel}: {text}")  # Debug log

            if "list summaries" in text:
                print("Processing 'list summaries' command")  # Debug log
                summaries = await query_service.get_all_summaries()
                print(f"Found summaries: {summaries}")  # Debug log
                response = format_summaries_response(summaries, channel)
                print(f"Sending response: {response}")  # Debug log
                return response

        return {"status": "ok"}

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        print(f"Error details: {type(e).__name__}")  # Debug log
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