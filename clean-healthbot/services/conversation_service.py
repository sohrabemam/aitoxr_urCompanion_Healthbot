from typing import List, Dict, Any
from core.config import supabase

async def get_conversation_history(conversation_id: str, limit: int = None) -> List[dict]:
    query = supabase.table("messages") \
        .select("user_input", "bot_response") \
        .eq("conversation_id", conversation_id) \
        .order("created_at", desc=True)
    if limit:
        query = query.limit(limit)
    response = query.execute()
    # Reverse to maintain chronological order
    return list(reversed(response.data))

async def update_conversation_scores_in_db(conversation_id: str, scores: Dict[str, Any]) -> bool:
    """Update conversation scores in Supabase"""
    try:
        supabase.table("conversations") \
            .update({"conversation_scores": scores}) \
            .eq("id", conversation_id) \
            .execute()
        return True
    except Exception as e:
        print(f"Error updating conversation scores: {e}")
        return False

def get_mood_dimensions() -> str :
    response = supabase.table("mood_dim") \
    .select("name,range").execute()
    mood_dimensions = response.data
    res = ""
    for dimension in mood_dimensions:
       res+=dimension["name"].lower()+" : float between "+str(dimension["range"])+","
    
    res = res[:-1]
    return res 