# app/models/chat.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    formatted_response: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None 