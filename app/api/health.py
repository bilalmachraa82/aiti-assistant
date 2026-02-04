"""
AITI Assistant - Health Check API
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.config import settings

logger = structlog.get_logger()
router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response."""
    status: str
    version: str
    timestamp: str
    components: dict


@router.get("/health", response_model=HealthStatus)
async def health_check(request: Request):
    """
    Check the health of the service and its components.
    """
    components = {}
    overall_status = "healthy"
    
    # Check vectorstore
    try:
        vectorstore = request.app.state.vectorstore
        stats = vectorstore.get_stats()
        components["vectorstore"] = {
            "status": "healthy",
            "document_count": stats["document_count"]
        }
    except Exception as e:
        components["vectorstore"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"
    
    # Check LLM configuration
    try:
        provider = settings.get_llm_provider()
        components["llm"] = {
            "status": "configured",
            "provider": provider,
            "model": settings.llm_model
        }
    except ValueError as e:
        components["llm"] = {"status": "not_configured", "error": str(e)}
        overall_status = "degraded"
    
    # Check Telegram bot
    if settings.telegram_bot_token:
        components["telegram"] = {"status": "configured"}
    else:
        components["telegram"] = {"status": "not_configured"}
    
    return HealthStatus(
        status=overall_status,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        components=components
    )


@router.get("/health/ready")
async def readiness_check(request: Request):
    """
    Kubernetes-style readiness probe.
    Returns 200 if the service is ready to accept traffic.
    """
    try:
        # Verify vectorstore is accessible
        vectorstore = request.app.state.vectorstore
        vectorstore.get_stats()
        
        # Verify LLM is configured
        settings.get_llm_provider()
        
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {"status": "not_ready", "reason": str(e)}


@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    Returns 200 if the service is alive.
    """
    return {"status": "alive"}


@router.get("/metrics")
async def metrics(request: Request):
    """
    Get service metrics.
    
    In production, consider using Prometheus client.
    """
    vectorstore = request.app.state.vectorstore
    stats = vectorstore.get_stats()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "vectorstore": {
            "document_count": stats["document_count"]
        },
        "config": {
            "llm_model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "chunk_size": settings.chunk_size,
            "top_k_results": settings.top_k_results
        }
    }
