"""
AITI Assistant - Embedding Service
Handles text embedding generation using OpenAI, Gemini, or local models.
"""

from typing import List
import openai
import google.generativeai as genai
import structlog

from app.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.model = settings.embedding_model
        self.provider = "gemini" if settings.gemini_api_key else "openai"
        self.client = None
        
        if settings.openai_api_key and settings.openai_api_key != "sk-your-openai-key":
            self.provider = "openai"
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
        elif settings.gemini_api_key:
            self.provider = "gemini"
            genai.configure(api_key=settings.gemini_api_key)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.provider == "openai":
            if not self.client:
                raise ValueError("OpenAI client not configured. Set OPENAI_API_KEY.")
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error("OpenAI embedding generation failed", error=str(e))
                raise
        
        elif self.provider == "gemini":
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text
                )
                return result['embedding']
            except Exception as e:
                logger.error("Gemini embedding generation failed", error=str(e))
                raise
        
        raise ValueError(f"Unknown embedding provider: {self.provider}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.provider == "openai":
            if not self.client:
                raise ValueError("OpenAI client not configured. Set OPENAI_API_KEY.")
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                sorted_data = sorted(response.data, key=lambda x: x.index)
                return [item.embedding for item in sorted_data]
            except Exception as e:
                logger.error("OpenAI batch embedding generation failed", error=str(e), count=len(texts))
                raise
        
        elif self.provider == "gemini":
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=texts
                )
                return result['embedding']
            except Exception as e:
                logger.error("Gemini batch embedding generation failed", error=str(e), count=len(texts))
                raise
        
        raise ValueError(f"Unknown embedding provider: {self.provider}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from the current model."""
        # Embedding dimensions by provider/model
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "text-embedding-004": 768  # Gemini
        }
        if self.provider == "gemini":
            return 768
        return dimensions.get(self.model, 1536)
