from typing import List, Dict, Any
from core.config import client, supabase
from models.mood import BotResponse, MoodDimensions
from utils.mood_helpers import get_mood_dimensions
import json

async def get_mental_health_response(user_input: str, conversation_history: List[dict] = None) -> BotResponse:
    """Get structured response from OpenAI with mood dimensions"""
    
    system_prompt = ("""Be blunt in your response. Dont hold back and dont sugar coat it . You are a blunt friend. Reply in the same language as user. If it is HINGLISH then reply in HINGLISH. Do not include any text before or after the JSON. Only output the JSON object. The numeric values should lie between the range of the mood dimensions for example (negative = sad/depressed, positive = happy/positive) , (0 = no stress, 10 = extremely stressed), (0 = no energy, 10 = very energetic),(0 = no motivation, 10 = very motivated),
     (0 = not lonely, 10 = very lonely),
    (0 = no confidence, 10 = very confident),
    (0 = no hope, 10 = very hopeful) ,
    mood dimensions are : """ + get_mood_dimensions() + """. An example of the json response is  stick to this format only , no other format is allowed:
{
  "content": "**Hello!** How are you feeling today?",
  "mood_dimensions": { "mood": 4, "stress": 1, "anxiety": 1, "energy": 6, "motivation": 7, "loneliness": 1, "confidence": 5, "hope": 7 }     
}
""")

    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        # Add recent conversation history (last 5 messages)
        recent_history = conversation_history[-5:]
        for msg in recent_history:
            messages.append({"role": "user", "content": msg["user_input"]})
            if msg.get("bot_response"):
                messages.append({"role": "assistant", "content": f"{msg['bot_response']['content']} \n\n Mood Dimensions: {msg['bot_response']['mood_dimensions']}"})
    
    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "system", "content": """ Be blunt , dont sugarcoat it. Keep langugage same as user. Output only json, stick to this format only , no other format is allowed:
{
  "content": "**Hello!** What's on your mind?",
  "mood_dimensions": { "mood": 4, "stress": 1, "anxiety": 1, "energy": 6, "motivation": 7, "loneliness": 1, "confidence": 5, "hope": 7 }     
}
"""})

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5,
            max_tokens=350
        )

        response_content = response.choices[0].message.content.strip()
        
        start=response_content.find("{")
        if start != -1:
            response_content = response_content[start:]
        
        try:
            response_data = json.loads(response_content)
            return BotResponse(**response_data)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {response_content}")
            # Fallback if JSON parsing fails
            return BotResponse(
                content="I'm here to listen and support you. How are you feeling today?",
                mood_dimensions=MoodDimensions(
                    mood=0.0,
                    stress=5.0,
                    anxiety=5.0,
                    energy=5.0,
                    motivation=5.0,
                    loneliness=5.0,
                    confidence=5.0,
                    hope=5.0
                )
            )
            
    except Exception as e:
        print(f"Error in get_mental_health_response: {e}")
        # Return default response on error
        return BotResponse(
            content="I'm here to listen and support you. How are you feeling today?",
            mood_dimensions=MoodDimensions(
                mood=0.0,
                stress=5.0,
                anxiety=5.0,
                energy=5.0,
                motivation=5.0,
                loneliness=5.0,
                confidence=5.0,
                hope=5.0
            )
        )

async def analyze_conversation_scores(conversation_id: str) -> Dict[str, Any]:
    """Analyze conversation and generate conversation scores using OpenAI"""
    
    # Get the last 10 messages for this conversation
    response = supabase.table("messages") \
        .select("user_input, bot_response") \
        .eq("conversation_id", conversation_id) \
        .order("created_at", desc=True) \
        .limit(10) \
        .execute()
    
    if not response.data:
        print(f"No messages found for conversation {conversation_id}")
        return {}
    
    conversation_text = ""
    for msg in reversed(response.data):
        conversation_text += f"User: {msg['user_input']}\n"
        if msg.get('bot_response'):
            conversation_text += f"Bot: {msg['bot_response']['content']}\n"

    prompt = f"""
    Analyze the following conversation and provide a summary of the user's emotional journey and key themes.
    The response should be a JSON object with the following keys: "summary", "average_mood_scores", "key_themes".
    "summary" should be a concise paragraph.
    "average_mood_scores" should be an object with the average score for each mood dimension.
    "key_themes" should be a list of strings.

    Conversation:
    {conversation_text}

    JSON Response:
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes conversations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        scores = json.loads(response.choices[0].message.content)
        return scores
        
    except Exception as e:
        print(f"Error analyzing conversation scores: {e}")
        return {} 