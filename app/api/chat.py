"""
AITI Assistant - Chat API
Endpoints for chatbot functionality.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
import structlog
import uuid
from datetime import datetime

from app.config import settings
from app.rag.chain import RAGChain

logger = structlog.get_logger()
router = APIRouter()


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., min_length=1, max_length=2000, description="The user's question")
    mode: str = Field("standard", description="Response mode: 'standard' or 'strict'")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous messages")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="The assistant's response")
    confidence: float = Field(..., description="Confidence score (0-1)")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    escalate: bool = Field(False, description="Whether to escalate to human")
    conversation_id: str = Field(..., description="Conversation ID for follow-ups")
    timestamp: str = Field(..., description="Response timestamp")


# In-memory conversation store (replace with database in production)
conversations: Dict[str, List[Dict[str, str]]] = {}


def get_rag_chain(request: Request) -> RAGChain:
    """Dependency to get RAG chain instance."""
    vectorstore = request.app.state.vectorstore
    return RAGChain(vectorstore)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_chain: RAGChain = Depends(get_rag_chain)
):
    """
    Process a chat message and return the assistant's response.
    
    The assistant uses RAG (Retrieval-Augmented Generation) to answer
    questions based on the indexed knowledge base.
    
    Modes:
    - **standard**: Uses retrieved context but can provide general responses
    - **strict**: Only responds based on retrieved documents, escalates otherwise
    """
    try:
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        history = request.conversation_history or conversations.get(conversation_id, [])
        
        logger.info(
            "Chat request received",
            query=request.query[:50],
            mode=request.mode,
            conversation_id=conversation_id
        )
        
        # Process query through RAG pipeline
        result = rag_chain.query(
            query=request.query,
            mode=request.mode,
            conversation_history=history
        )
        
        # Update conversation history
        history.append({"role": "user", "content": request.query})
        history.append({"role": "assistant", "content": result["response"]})
        conversations[conversation_id] = history[-10:]  # Keep last 10 messages
        
        logger.info(
            "Chat response generated",
            confidence=result["confidence"],
            sources_count=len(result["sources"]),
            escalate=result["escalate"]
        )
        
        return ChatResponse(
            response=result["response"],
            confidence=result["confidence"],
            sources=result["sources"],
            escalate=result["escalate"],
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error("Chat request failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history by ID."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }


@router.delete("/chat/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id in conversations:
        del conversations[conversation_id]
    
    return {"status": "deleted", "conversation_id": conversation_id}


@router.post("/chat/feedback")
async def submit_feedback(
    conversation_id: str,
    message_index: int,
    rating: int = Field(..., ge=1, le=5),
    comment: Optional[str] = None
):
    """
    Submit feedback for a response.
    
    This helps improve the system over time.
    """
    logger.info(
        "Feedback received",
        conversation_id=conversation_id,
        message_index=message_index,
        rating=rating
    )
    
    # In production, store feedback in database
    return {
        "status": "received",
        "conversation_id": conversation_id,
        "rating": rating
    }
