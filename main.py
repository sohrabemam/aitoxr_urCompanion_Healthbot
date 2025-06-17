from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import conversations, messages

app = FastAPI(title="Mental Health Chat API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(conversations.router, tags=["Conversations"])
app.include_router(messages.router, tags=["Messages"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Mental Health Chat API"} 