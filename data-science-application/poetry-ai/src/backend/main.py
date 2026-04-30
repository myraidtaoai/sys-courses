from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import logging
from backend.graph.poetry_graph import poetry_graph_app  # Import the graph application

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS to allow requests from the frontend
origins = [
    "http://localhost:3000",  # Standard React port
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    thread_id: str
    response: str
    interrupted: bool = False
    next_step: Optional[str] = None
    execution_steps: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ResumeRequest(BaseModel):
    poem_text: str
    thread_id: str

class ResumeResponse(BaseModel):
    response: str

# --- Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Generate a new thread_id if one isn't provided
    thread_id = request.thread_id or str(uuid.uuid4())
    
    user_query = request.query.lower()
    logger.info(f"\n{'='*80}")
    logger.info(f"[API] Chat Request - Thread: {thread_id}, Query: '{user_query}'")
    logger.info(f"{'='*80}\n")
    
    # Prepare state for the graph
    initial_state = {"query": user_query, "thread_id": thread_id, "response": "", "poem_text": None}
    
    # Run the graph (invoke)
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = poetry_graph_app.graph.invoke(initial_state, config=config)
        
        # Extract response from graph state
        response_text = result.get("response", "I'm not sure how to respond to that.")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[API] Chat Complete - Thread: {thread_id}")
        logger.info(f"[API] Final Response: {response_text[:200]}...")
        logger.info(f"{'='*80}\n")
        
        return ChatResponse(
            thread_id=thread_id,
            response=response_text,
            interrupted=False,
            execution_steps=result
        )
    except Exception as e:
        logger.error(f"\n[API] Error during chat execution: {e}\n")
        return ChatResponse(
            thread_id=thread_id,
            response="An error occurred while processing your request.",
            interrupted=False,
            error=str(e)
        )

@app.post("/resume", response_model=ResumeResponse)
async def resume_endpoint(request: ResumeRequest):
    # Mock logic: Handle the input provided during interruption
    snippet = request.poem_text[:50]
    return ResumeResponse(
        response=f"Thank you. I have processed the poem starting with: '{snippet}...'."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)