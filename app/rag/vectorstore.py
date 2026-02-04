"""
AITI Assistant - Vector Store
ChromaDB-based vector storage for document chunks.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
import structlog

from app.config import settings
from app.rag.embeddings import EmbeddingService

logger = structlog.get_logger()


class VectorStore:
    """Vector store for document retrieval using ChromaDB."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_dir = persist_directory or settings.chroma_persist_dir
        
        # Ensure directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name="aiti_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService()
        
        logger.info(
            "Vector store initialized",
            persist_dir=self.persist_dir,
            document_count=self.collection.count()
        )
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts (chunks)
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        # Generate IDs if not provided
        if not ids:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Add to collection
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("Documents added to vector store", count=len(texts))
        return ids
    
    def search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of results with document, metadata, and score
        """
        top_k = top_k or settings.top_k_results
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    "id": results['ids'][0][i] if results['ids'] else None,
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "score": 1 - results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by ID.
        
        Args:
            ids: List of document IDs to delete
        """
        self.collection.delete(ids=ids)
        logger.info("Documents deleted from vector store", count=len(ids))
    
    def clear(self) -> None:
        """Clear all documents from the vector store."""
        # Delete and recreate collection
        self.client.delete_collection("aiti_documents")
        self.collection = self.client.create_collection(
            name="aiti_documents",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "document_count": self.collection.count(),
            "persist_directory": self.persist_dir
        }
