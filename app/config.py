"""
AITI Assistant - Configuration
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(None, alias="GEMINI_API_KEY")
    llm_model: str = Field("gpt-4o-mini", alias="LLM_MODEL")
    embedding_model: str = Field("text-embedding-3-small", alias="EMBEDDING_MODEL")
    
    # Database
    database_url: str = Field("sqlite:///./data/aiti.db", alias="DATABASE_URL")
    chroma_persist_dir: str = Field("./data/vectorstore", alias="CHROMA_PERSIST_DIR")
    
    # Telegram
    telegram_bot_token: Optional[str] = Field(None, alias="TELEGRAM_BOT_TOKEN")
    
    # Server
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")
    debug: bool = Field(False, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    # RAG Configuration
    chunk_size: int = Field(500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(50, alias="CHUNK_OVERLAP")
    top_k_results: int = Field(5, alias="TOP_K_RESULTS")
    confidence_threshold: float = Field(0.7, alias="CONFIDENCE_THRESHOLD")
    
    # Security
    api_key: Optional[str] = Field(None, alias="API_KEY")
    cors_origins: str = Field("*", alias="CORS_ORIGINS")
    
    # Company Configuration
    company_name: str = Field("Empresa", alias="COMPANY_NAME")
    company_language: str = Field("pt-PT", alias="COMPANY_LANGUAGE")
    system_prompt: str = Field(
        "És um assistente de atendimento ao cliente da {company}. "
        "Respondes apenas com base no contexto fornecido. "
        "Se não souberes, diz que vais encaminhar para um colega. "
        "Sê simpático, profissional e conciso.",
        alias="SYSTEM_PROMPT"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def formatted_system_prompt(self) -> str:
        """Get system prompt with company name inserted."""
        return self.system_prompt.replace("{company}", self.company_name)
    
    def get_llm_provider(self) -> str:
        """Determine which LLM provider to use."""
        if self.openai_api_key and self.openai_api_key.startswith("sk-"):
            return "openai"
        elif self.anthropic_api_key and self.anthropic_api_key.startswith("sk-ant"):
            return "anthropic"
        elif self.gemini_api_key:
            return "gemini"
        raise ValueError("No LLM API key configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY.")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
