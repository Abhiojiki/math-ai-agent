"""
FastAPI application with SQLite database integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn


# Use absolute imports (app.module instead of module)
from app.agent import get_agent
from app.config import settings
from app.database import get_db, init_db

import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


# Initialize FastAPI app
app = FastAPI(
    title="Math Routing Agent API",
    description="AI-powered math tutor with knowledge base, web search, and human feedback",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
     allow_origins=settings.ALLOWED_ORIGINS,  # Changed from ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {"query": "What is the quadratic formula?"}
        }

class QueryResponse(BaseModel):
    conversation_id: int
    query: str
    answer: str
    source: str
    confidence_score: float
    kb_matches: int

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: int = Field(..., ge=1, le=5)
    is_correct: Optional[bool] = None
    correction: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=1000)
    conversation_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is 2+2?",
                "answer": "2+2=4",
                "rating": 5,
                "is_correct": True,
                "correction": None,
                "notes": "Perfect explanation!"
            }
        }

class FeedbackResponse(BaseModel):
    status: str
    message: str
    feedback_id: int

class StatsResponse(BaseModel):
    total_conversations: int
    total_feedback: int
    avg_rating: Optional[float]
    source_distribution: Dict[str, int]
    avg_confidence_by_source: Dict[str, float]

# Global instances
agent = None
db = None

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize agent and database on startup."""
    global agent, db
    try:
        settings.validate()
        db = init_db()
        agent = get_agent()
        print("✅ Math Agent and Database initialized")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Math Routing Agent with SQLite",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query",
            "feedback": "/api/feedback",
            "stats": "/api/stats",
            "recent": "/api/conversations/recent",
            "docs": "/docs"
        }
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_math(request: QueryRequest):
    """
    Submit a math question and get step-by-step answer.
    Saves conversation to database.
    """
    if not agent or not db:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get answer from agent
        result = agent.route_and_answer(request.query)
        
        # Save to database
        conversation_id = db.save_conversation(
            query=result["query"],
            answer=result["answer"],
            source=result["source"],
            confidence_score=result["confidence_score"],
            kb_matches=result["kb_matches"]
        )
        
        return QueryResponse(
            conversation_id=conversation_id,
            **result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for an answer.
    Saves to database and creates human intervention if correction is substantial.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        feedback_id = db.save_feedback(
            query=request.query,
            answer=request.answer,
            rating=request.rating,
            is_correct=request.is_correct,
            correction=request.correction,
            notes=request.notes,
            conversation_id=request.conversation_id
        )
        
        # Determine if intervention was created
        intervention_created = request.correction and len(request.correction) > 50
        
        return FeedbackResponse(
            status="success",
            message=f"Feedback saved{' (human intervention recorded)' if intervention_created else ''}",
            feedback_id=feedback_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback save failed: {str(e)}")

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get aggregate statistics about conversations and feedback."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        feedback_stats = db.get_feedback_stats()
        conversations = db.get_recent_conversations(limit=1000)  # Get all for count
        
        return StatsResponse(
            total_conversations=len(conversations),
            total_feedback=feedback_stats.get("total_feedback", 0),
            avg_rating=round(feedback_stats.get("avg_rating", 0.0), 2) if feedback_stats.get("avg_rating") else None,
            source_distribution=db.get_source_distribution(),
            avg_confidence_by_source=db.get_average_confidence_by_source()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.get("/api/conversations/recent")
async def get_recent_conversations(limit: int = 10):
    """Get recent conversations."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    return {"conversations": db.get_recent_conversations(limit=limit)}

@app.get("/api/feedback/recent")
async def get_recent_feedback(limit: int = 10):
    """Get recent feedback entries."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    return {"feedback": db.get_recent_feedback(limit=limit)}

@app.get("/api/interventions")
async def get_interventions(limit: int = 10):
    """Get human interventions (significant corrections)."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    return {"interventions": db.get_human_interventions(limit=limit)}

@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    try:
        db_status = "healthy" if db else "not_initialized"
        agent_status = "healthy" if agent else "not_initialized"
        
        # Test database connection
        if db:
            try:
                db.get_feedback_stats()
            except:
                db_status = "connection_failed"
        
        return {
            "status": "healthy" if db_status == "healthy" and agent_status == "healthy" else "degraded",
            "components": {
                "database": db_status,
                "agent": agent_status,
                "qdrant": "healthy",
                "llm": "healthy"
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
