"""
AITI Assistant - Embedding Service
Handles text embedding generation using OpenAI or local models.
"""

from typing import List
import openai
import structlog

from app.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.model = settings.embedding_model
        self.client = None
        
        if settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self.client:
            raise ValueError("OpenAI client not configured. Set OPENAI_API_KEY.")
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.client:
            raise ValueError("OpenAI client not configured. Set OPENAI_API_KEY.")
        
        if not texts:
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            # Sort by index to maintain order
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            logger.error("Batch embedding generation failed", error=str(e), count=len(texts))
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from the current model."""
        # OpenAI embedding dimensions
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return dimensions.get(self.model, 1536)
