from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    thread_id: str
    response: str
    interrupted: bool = False
    next_step: Optional[str] = None

class ResumeRequest(BaseModel):
    poem_text: str
    thread_id: str

class ResumeResponse(BaseModel):
    response: str