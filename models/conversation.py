from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    first_message: str

class Conversation(ConversationBase):
    id: str
    user_id: str
    conversation_scores: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 