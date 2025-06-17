from datetime import datetime, timedelta
from fastapi import HTTPException
from core.config import supabase

# Rate limiting helper
async def check_rate_limit(user_id: str, is_paid: bool = False):
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    # Query messages in the last hour
    response = supabase.table("messages") \
        .select("id") \
        .eq("user_id", user_id) \
        .gte("created_at", one_hour_ago.isoformat()) \
        .execute()
    
    print("response.data in check rate limit", response.data)
    message_count = len(response.data)
    limit = 50 if is_paid else 50
    
    if message_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} messages per hour."
        ) 