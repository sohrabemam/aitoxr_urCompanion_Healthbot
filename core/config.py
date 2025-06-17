import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.client import ClientOptions
import openai

# Load environment variables
load_dotenv()

# Initialize Supabase client
opts = ClientOptions().replace(schema="chat")
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", ""),
    options=opts
)

# Initialize OpenAI client
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) 