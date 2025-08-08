from core.config import supabase

def get_mood_dimensions() -> str :
    response = supabase.table("mood_dim") \
    .select("name,range").execute()
    mood_dimensions = response.data
    res = ""
    for dimension in mood_dimensions:
       res+=dimension["name"].lower()+" : float between "+str(dimension["range"])+","
    
    res = res[:-1]
    return res 