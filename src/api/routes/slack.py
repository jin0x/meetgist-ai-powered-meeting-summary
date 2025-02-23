from fastapi import APIRouter, Depends
from ..models.slack import SlackEvent, SlackChallenge
from ..services.query import QueryService
from typing import Union

router = APIRouter()

@router.post("/slack/events")
async def slack_events(
    event: Union[SlackEvent, SlackChallenge],
    query_service: QueryService = Depends(QueryService)
) -> dict:
    """Handle Slack events"""

    # Handle URL verification
    if hasattr(event, 'challenge'):
        return {"challenge": event.challenge}

    # Handle mention events
    if event.event.type == "app_mention":
        command_text = event.event.text.lower()

        # Simple command handling for now
        if "list summaries" in command_text:
            summaries = await query_service.get_all_summaries()
            return {
                "type": "message",
                "channel": event.event.channel,
                "text": format_summaries_response(summaries)
            }

        elif "list meetings" in command_text:
            meetings = await query_service.get_all_meetings()
            return {
                "type": "message",
                "channel": event.event.channel,
                "text": format_meetings_response(meetings)
            }

    return {"status": "ok"}

def format_summaries_response(summaries: list) -> str:
    """Format summaries list for Slack response"""
    if not summaries:
        return "No summaries found."

    response = "📝 *Available Summaries:*\n"
    for summary in summaries:
        response += f"• {summary['meeting_title']} ({summary['created_at']})\n"
    return response

def format_meetings_response(meetings: list) -> str:
    """Format meetings list for Slack response"""
    if not meetings:
        return "No meetings found."

    response = "📅 *Available Meetings:*\n"
    for meeting in meetings:
        response += f"• {meeting['meeting_title']}\n"
    return response