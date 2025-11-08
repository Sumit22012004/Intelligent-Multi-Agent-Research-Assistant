"""
Core configuration settings for the research assistant.
Loads environment variables and provides typed configuration.
"""

from pydantic_settings import BaseSettings
from loguru import logger


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str
    perplexity_api_key: str
    
    # MongoDB Configuration
    mongodb_uri: str
    mongodb_db_name: str
    
    # Qdrant Configuration
    qdrant_host: str
    qdrant_port: int
    qdrant_path: str
    
    # HuggingFace Configuration
    hf_model_name: str
    hf_cache_dir: str
    
    # Application Settings
    user_id: str
    app_env: str
    log_level: str
    max_upload_size_mb: int
    chunk_size: int
    chunk_overlap: int
    
    # Backend Configuration
    backend_host: str
    backend_port: int
    
    # Frontend Configuration
    streamlit_port: int
    backend_url: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_settings() -> Settings:
    """Load and return application settings."""
    settings = Settings()
    logger.info(f"Settings loaded for environment: {settings.app_env}")
    return settings


# Global settings instance
settings = load_settings()

