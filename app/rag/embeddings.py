"""
AITI Assistant - Embedding Service
Handles text embedding generation using OpenAI, Gemini, or local models.
"""

from typing import List
import openai
import structlog

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.model = settings.embedding_model
        self.provider = "none"
        self.client = None
        
        # Determine provider based on available keys
        if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
            self.provider = "openai"
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
        elif settings.gemini_api_key and GEMINI_AVAILABLE:
            self.provider = "gemini"
            genai.configure(api_key=settings.gemini_api_key)
        
        logger.info(f"Embedding service initialized with provider: {self.provider}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.provider == "openai":
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
                    model="models/embedding-001",
                    content=text
                )
                return result['embedding']
            except Exception as e:
                logger.error("Gemini embedding generation failed", error=str(e))
                raise
        
        raise ValueError(f"No embedding provider configured. Set OPENAI_API_KEY or GEMINI_API_KEY.")
    
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
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                sorted_data = sorted(response.data, key=lambda x: x.index)
                return [item.embedding for item in sorted_data]
            except Exception as e:
                logger.error("OpenAI batch embedding failed", error=str(e), count=len(texts))
                raise
        
        elif self.provider == "gemini":
            try:
                # Gemini batch embedding
                embeddings = []
                for text in texts:
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=text
                    )
                    embeddings.append(result['embedding'])
                return embeddings
            except Exception as e:
                logger.error("Gemini batch embedding failed", error=str(e), count=len(texts))
                raise
        
        raise ValueError(f"No embedding provider configured. Set OPENAI_API_KEY or GEMINI_API_KEY.")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from the current model."""
        if self.provider == "gemini":
            return 768  # Gemini text-embedding-004 dimension
        
        # OpenAI embedding dimensions
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return dimensions.get(self.model, 1536)
