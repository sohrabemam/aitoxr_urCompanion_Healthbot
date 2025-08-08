from pydantic import BaseModel

class MoodDimensions(BaseModel):
    mood: float  # [-5, 5]
    stress: float  # [0, 10]
    anxiety: float  # [0, 10]
    energy: float  # [0, 10]
    motivation: float  # [0, 10]
    loneliness: float  # [0, 10]
    confidence: float  # [0, 10]
    hope: float  # [0, 10]

class BotResponse(BaseModel):
    content: str
    mood_dimensions: MoodDimensions 