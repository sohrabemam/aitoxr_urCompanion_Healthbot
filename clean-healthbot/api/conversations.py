from fastapi import APIRouter, HTTPException
from models.conversation import Conversation, ConversationCreate
from services.openai_service import analyze_conversation_scores, get_mental_health_response
from services.conversation_service import update_conversation_scores_in_db
from core.config import supabase
from typing import List, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/conversations/", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate,
    user_id: str,
    is_paid: bool = False
):
    """
    Creates a new conversation.
    - Generates a title if not provided.
    - Creates a new conversation record in the database.
    - Creates the first message in the conversation.
    """
    # Generate a title if not provided
    title = conversation.title
    if not title:
        title = f"Chat on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

    # Create new conversation
    new_conversation_id = str(uuid.uuid4())
    
    try:
        conv_data = supabase.table("conversations").insert({
            "id": new_conversation_id,
            "user_id": user_id,
            "title": title
        }).execute().data[0]

        # Create first message
        bot_response = await get_mental_health_response(conversation.first_message, [])
    
        supabase.table("messages").insert({
            "conversation_id": new_conversation_id,
            "user_id": user_id,
            "user_input": conversation.first_message,
            "bot_response": bot_response.model_dump(),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return Conversation(**conv_data)
        
    except Exception as e:
        print(f"Error creating conversation: {e}")
        # If something fails, we should probably delete the conversation record
        supabase.table("conversations").delete().eq("id", new_conversation_id).execute()
        raise HTTPException(status_code=500, detail="Failed to create conversation.")

@router.post("/conversations/{conversation_id}/analyze")
async def analyze_conversation_endpoint(conversation_id: str, user_id: str):
    """
    Analyzes the conversation and updates the scores in the database.
    - Fetches user data to verify ownership.
    - Analyzes conversation scores.
    - Updates scores in the database.
    """
    # Verify user owns conversation
    conv_response = supabase.table("conversations").select("user_id").eq("id", conversation_id).execute()
    if not conv_response.data or conv_response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    scores = await analyze_conversation_scores(conversation_id)
    if not scores:
        raise HTTPException(status_code=500, detail="Failed to analyze conversation.")
        
    success = await update_conversation_scores_in_db(conversation_id, scores)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update conversation scores.")
        
    return {"status": "success", "scores": scores}


@router.get("/conversations/{conversation_id}/scores")
async def get_conversation_scores(conversation_id: str, user_id: str):
    """
    Retrieves the conversation scores for a given conversation.
    - Verifies that the user owns the conversation.
    """
    response = supabase.table("conversations") \
        .select("conversation_scores, user_id") \
        .eq("id", conversation_id) \
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return response.data[0]['conversation_scores']


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, user_id: str):
    """
    Retrieves all messages for a given conversation.
    - Verifies that the user owns the conversation.
    """
    # Verify user owns conversation
    conv_response = supabase.table("conversations").select("user_id").eq("id", conversation_id).execute()
    if not conv_response.data or conv_response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    response = supabase.table("messages") \
        .select("*") \
        .eq("conversation_id", conversation_id) \
        .order("created_at") \
        .execute()
        
    return response.data

@router.get("/conversations/")
async def get_user_conversations(user_id: str) -> List[Conversation]:
    """
    Retrieves all conversations for a given user.
    """
    response = supabase.table("conversations") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()
        
    return [Conversation(**conv) for conv in response.data] 