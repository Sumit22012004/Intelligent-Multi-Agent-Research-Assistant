"""HuggingFace embedding service for text vectorization."""

from sentence_transformers import SentenceTransformer
from loguru import logger
from backend.core.config import settings


class EmbeddingService:
    """Handles text embedding generation using HuggingFace models."""
    
    def __init__(self):
        self.model: SentenceTransformer = None
        self.model_name = settings.hf_model_name
        self.cache_dir = settings.hf_cache_dir
        self.vector_size = 384  # Size for all-MiniLM-L6-v2
        self.is_loaded = False
    
    def load_model(self):
        """Load the embedding model."""
        try:
            logger.info(f"Loading embedding model: {settings.hf_model_name}")
            
            self.model = SentenceTransformer(
                settings.hf_model_name,
                cache_folder=settings.hf_cache_dir
            )
            
            self.is_loaded = True
            logger.info("Embedding model loaded successfully")
            
        except Exception as error:
            logger.error(f"Failed to load embedding model: {error}")
            raise
    
    async def create_embedding(self, text: str) -> list[float]:
        """Create embedding vector for given text."""
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
            
        except Exception as error:
            logger.error(f"Failed to create embedding: {error}")
            raise
    
    async def create_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for multiple texts."""
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
            
        except Exception as error:
            logger.error(f"Failed to create batch embeddings: {error}")
            raise
    
    def get_vector_size(self) -> int:
        """Get the size of embedding vectors."""
        return self.vector_size


# Global embedding service instance
embedding_service = EmbeddingService()

