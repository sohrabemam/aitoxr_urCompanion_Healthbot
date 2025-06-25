from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .mood import BotResponse

class MessageBase(BaseModel):
    user_input: str

class MessageCreate(MessageBase):
    conversation_id: str

class Message(MessageBase):
    id: int
    conversation_id: str
    user_id: str
    bot_response: Optional[BotResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    content: str
    remaining_responses: int 