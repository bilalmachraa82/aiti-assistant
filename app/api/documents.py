"""
AITI Assistant - Documents API
Endpoints for document management.
"""

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel, Field
import structlog

from app.config import settings

logger = structlog.get_logger()
router = APIRouter()


# Models
class DocumentInfo(BaseModel):
    """Document information model."""
    id: str
    filename: str
    file_type: str
    size_bytes: int
    chunks_count: int
    status: str
    created_at: str


class DocumentsStats(BaseModel):
    """Documents statistics."""
    total_documents: int
    total_chunks: int
    file_types: dict


# In-memory document registry (replace with database in production)
documents_registry: dict = {}


@router.post("/documents/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    category: Optional[str] = Form(None)
):
    """
    Upload a new document for indexing.
    
    Supported formats: PDF, DOCX, TXT, MD, CSV
    Maximum size: 10MB
    """
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".txt", ".md", ".csv"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (10MB max)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")
    
    # Save file
    documents_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "documents")
    os.makedirs(documents_dir, exist_ok=True)
    
    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(documents_dir, safe_filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    logger.info(
        "Document uploaded",
        doc_id=doc_id,
        filename=file.filename,
        size=len(content)
    )
    
    # Register document (in production, would trigger async indexing)
    documents_registry[doc_id] = {
        "id": doc_id,
        "filename": file.filename,
        "file_type": file_ext,
        "size_bytes": len(content),
        "file_path": file_path,
        "category": category,
        "status": "uploaded",  # pending_indexing, indexed, error
        "created_at": __import__("datetime").datetime.utcnow().isoformat()
    }
    
    # TODO: Trigger async indexing via background task or queue
    # For demo, we'll return immediately
    
    return {
        "status": "success",
        "document": documents_registry[doc_id],
        "message": "Document uploaded. Run 'python -m app.ingest' to index."
    }


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(request: Request):
    """List all indexed documents."""
    vectorstore = request.app.state.vectorstore
    stats = vectorstore.get_stats()
    
    # Get documents from registry
    docs = []
    for doc_id, doc in documents_registry.items():
        docs.append(DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            size_bytes=doc["size_bytes"],
            chunks_count=0,  # Would get from vectorstore metadata
            status=doc["status"],
            created_at=doc["created_at"]
        ))
    
    return docs


@router.get("/documents/stats")
async def get_documents_stats(request: Request):
    """Get statistics about indexed documents."""
    vectorstore = request.app.state.vectorstore
    stats = vectorstore.get_stats()
    
    # Count file types
    file_types = {}
    for doc in documents_registry.values():
        ext = doc["file_type"]
        file_types[ext] = file_types.get(ext, 0) + 1
    
    return {
        "total_documents": len(documents_registry),
        "total_chunks": stats["document_count"],
        "file_types": file_types,
        "persist_directory": stats["persist_directory"]
    }


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get details of a specific document."""
    if doc_id not in documents_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return documents_registry[doc_id]


@router.delete("/documents/{doc_id}")
async def delete_document(request: Request, doc_id: str):
    """
    Delete a document and its chunks from the index.
    """
    if doc_id not in documents_registry:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents_registry[doc_id]
    
    # Delete file
    if os.path.exists(doc["file_path"]):
        os.remove(doc["file_path"])
    
    # Delete from vectorstore (would need to track chunk IDs)
    # vectorstore.delete_documents(chunk_ids)
    
    # Remove from registry
    del documents_registry[doc_id]
    
    logger.info("Document deleted", doc_id=doc_id)
    
    return {"status": "deleted", "doc_id": doc_id}


@router.post("/documents/reindex")
async def reindex_all(request: Request):
    """
    Re-index all documents.
    
    This clears the vectorstore and re-processes all documents.
    """
    # In production, this would be a background task
    logger.info("Reindex requested")
    
    return {
        "status": "scheduled",
        "message": "Run 'python -m app.ingest --reset' to reindex all documents."
    }
