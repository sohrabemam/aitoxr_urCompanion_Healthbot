from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.message import MessageCreate, ChatResponse
from models.mood import BotResponse
from services.openai_service import get_mental_health_response
from services.conversation_service import get_conversation_history, update_conversation_scores_in_db
from services.openai_service import analyze_conversation_scores
from utils.rate_limiter import check_rate_limit
from core.config import supabase
from datetime import datetime
import json

router = APIRouter()

async def run_analysis_and_update(conversation_id: str):
    """Background task to run conversation analysis and update scores"""
    scores = await analyze_conversation_scores(conversation_id)
    if scores:
        await update_conversation_scores_in_db(conversation_id, scores)

@router.post("/messages/", response_model=ChatResponse)
async def create_message(
    message: MessageCreate,
    user_id: str,
    background_tasks: BackgroundTasks,
    is_paid: bool = False
):
    """
    Create a new message in a conversation.
    - Checks rate limit for the user.
    - Retrieves conversation history.
    - Gets a response from the mental health bot.
    - Saves the new message and bot response to the database.
    - Triggers a background task to analyze conversation scores.
    """
    remaining_responses = await check_rate_limit(user_id, is_paid)
    
    history_limit = 15 if is_paid else 5
    conversation_history = await get_conversation_history(message.conversation_id, limit=history_limit)
    
    bot_response: BotResponse = await get_mental_health_response(
        message.user_input,
        conversation_history
    )
    
    # Save message to database
    try:
        supabase.table("messages").insert({
            "conversation_id": message.conversation_id,
            "user_id": user_id,
            "user_input": message.user_input,
            "bot_response": bot_response.model_dump(),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        # Trigger background analysis after every 5 messages
        if len(conversation_history) % 5 == 0 and len(conversation_history) > 0:
            background_tasks.add_task(run_analysis_and_update, message.conversation_id)
            
        return ChatResponse(content=bot_response.content, remaining_responses=remaining_responses - 1)
        
    except Exception as e:
        print(f"Error saving message: {e}")
        raise HTTPException(status_code=500, detail="Failed to save message.") 