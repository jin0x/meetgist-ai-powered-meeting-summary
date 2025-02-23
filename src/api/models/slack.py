from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SlackEventBase(BaseModel):
    """Base model for Slack events"""
    type: str
    event_ts: str = Field(..., description="Event timestamp")

class SlackMentionEvent(SlackEventBase):
    """Model for app_mention events"""
    user: str = Field(..., description="User ID who mentioned the bot")
    text: str = Field(..., description="Message text")
    channel: str = Field(..., description="Channel ID where mention occurred")

class SlackChallenge(BaseModel):
    """Model for Slack URL verification"""
    token: str
    challenge: str
    type: str

class SlackEvent(BaseModel):
    """Main event wrapper"""
    token: str
    team_id: str
    event: SlackMentionEvent
    event_id: str
    event_time: int