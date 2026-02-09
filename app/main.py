"""
AITI Assistant - Main FastAPI Application
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import structlog

from app.config import settings
from app.api import chat, documents, health
from app.api import direct_chat

try:
    from app.rag.vectorstore import VectorStore
    VECTORSTORE_AVAILABLE = True
except Exception:
    VECTORSTORE_AVAILABLE = False

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AITI Assistant", version="1.0.0")
    
    # Initialize vector store (optional - falls back to direct chat)
    if VECTORSTORE_AVAILABLE:
        try:
            app.state.vectorstore = VectorStore()
            logger.info("Vector store initialized", persist_dir=settings.chroma_persist_dir)
        except Exception as e:
            logger.warning(f"Vector store init failed, using direct chat: {e}")
            app.state.vectorstore = None
    else:
        logger.info("VectorStore not available, using direct Gemini chat")
        app.state.vectorstore = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down AITI Assistant")


# Create FastAPI app
app = FastAPI(
    title="AITI Assistant",
    description="Assistente Virtual Inteligente com RAG para Atendimento ao Cliente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(direct_chat.router, prefix="/api/v2", tags=["Direct Chat"])
app.include_router(chat.router, prefix="/api", tags=["Chat (RAG)"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(health.router, prefix="/api", tags=["Health"])

# Serve static files (widget)
widget_path = os.path.join(os.path.dirname(__file__), "..", "widget")
if os.path.exists(widget_path):
    app.mount("/widget", StaticFiles(directory=widget_path), name="widget")


@app.get("/")
async def root():
    """Root endpoint - redirect to demo."""
    return RedirectResponse(url="/demo")


@app.get("/demo")
async def demo():
    """Serve the premium demo page."""
    demo_path = os.path.join(widget_path, "demo-premium.html")
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    return {"error": "Demo page not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
