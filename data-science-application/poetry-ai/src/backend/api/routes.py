from fastapi import APIRouter
import uuid
from .schemas import ChatRequest, ChatResponse, ResumeRequest, ResumeResponse
from ..graph.poetry_graph import poetry_graph_app

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handles a chat query, invokes the graph, and returns a response.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    user_query = request.query.lower()
    
    # Prepare state for the graph
    initial_state = {"query": user_query, "thread_id": thread_id}
    config = {"configurable": {"thread_id": thread_id}}

    # Invoke the graph
    result = poetry_graph_app.graph.invoke(initial_state, config=config)
    response_text = result.get("response", "I'm not sure how to respond to that.")

    # Detect if execution was interrupted (waiting for input)
    is_interrupted = "provide the text of the poem" in response_text.lower()

    return ChatResponse(
        thread_id=thread_id,
        response=response_text,
        interrupted=is_interrupted,
        next_step="poem_input" if is_interrupted else None,
    )

@router.post("/resume", response_model=ResumeResponse)
async def resume_endpoint(request: ResumeRequest):
    """
    Resumes an interrupted graph execution (e.g., after poem submission).
    NOTE: This is mock logic and needs to be implemented to resume the graph.
    """
    snippet = request.poem_text[:50]
    return ResumeResponse(
        response=f"Thank you. I have processed the poem starting with: '{snippet}...'."
    )