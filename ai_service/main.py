# ai_service/main.py
# The FastAPI server — this is what runs and accepts HTTP requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent import run_agent
from rag import build_vector_store
import os
from pydantic import BaseModel, Field

app = FastAPI(
    title="StayLink AI Service",
    description="AI agent for property search and recommendations",
    version="1.0.0"
)

# CORS — allows your React frontend to call this API
# Without this, browser blocks the request
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================
# Data Models (Pydantic)
# These define what JSON shape the API expects/returns
# Like Django serializers but simpler
# ========================

class Message(BaseModel):
    """A single chat message"""
    role: str       # "user" or "assistant"
    content: str    # the message text


class ChatRequest(BaseModel):
    """What the frontend sends to /chat"""
    message: str                              # current user message
    chat_history: Optional[List[Message]] = Field(default_factory=list) # previous messages


class ChatResponse(BaseModel):
    """What /chat returns to the frontend"""
    reply: str


# ========================
# API ENDPOINTS
# ========================

@app.get("/")
def health_check():
    """
    Simple check to see if the service is running.
    Visit http://localhost:8001/ to verify.
    """
    return {
        "status": "running",
        "service": "StayLink AI Service"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint — called by React frontend.
    
    Receives user message + chat history.
    Returns AI response.
    
    Example request:
    POST http://localhost:8001/chat
    {
        "message": "I want a villa in Kochi under ₹3000",
        "chat_history": []
    }
    
    Example response:
    {
        "reply": "I found 2 villas in Kochi under ₹3000!..."
    }
    """
    try:
        # Convert Pydantic models to plain dicts for OpenAI
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]

        reply = run_agent(
            user_message=request.message,
            chat_history=history
        )

        return ChatResponse(reply=reply)

    except Exception as e:
        print(f"❌ Error in /chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )


@app.post("/rebuild-index")
def rebuild_index():
    """
    Rebuilds the ChromaDB property index.
    
    Call this when:
    - New properties are added in Django
    - Property details are updated
    - You want to refresh the AI's knowledge
    
    Django calls this automatically via signals (Step 13).
    You can also call it manually anytime.
    """
    try:
        build_vector_store()
        return {
            "message": "✅ Property index rebuilt successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/health/django")
def check_django_connection():
    """
    Tests if Django API is reachable from AI service.
    Useful for debugging connection issues.
    """
    import requests
    django_url = os.getenv("DJANGO_API_BASE_URL")
    try:
        response = requests.get(
            f"{django_url}/api/owner/public/properties/",
            timeout=5
        )
        return {
            "django_status": "connected",
            "properties_count": len(response.json())
        }
    except Exception as e:
        return {
            "django_status": "error",
            "detail": str(e)
        }