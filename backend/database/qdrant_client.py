"""Qdrant vector database client and operations."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from loguru import logger
from backend.core.config import settings


class QdrantConnection:
    """Manages Qdrant vector database connection and operations."""
    
    def __init__(self):
        self.client: QdrantClient = None
        self.collection_name = f"user_{settings.user_id}"
    
    def connect(self):
        """Connect to Qdrant database."""
        try:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port
            )
            
            # Test connection
            collections = self.client.get_collections()
            logger.info(f"Connected to Qdrant. Collections: {len(collections.collections)}")
            
        except Exception as error:
            logger.error(f"Failed to connect to Qdrant: {error}")
            raise
    
    def create_collection_if_not_exists(self, vector_size: int = 384):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")
        else:
            logger.info(f"Qdrant collection already exists: {self.collection_name}")
    
    def get_client(self) -> QdrantClient:
        """Get Qdrant client instance."""
        if self.client is None:
            raise ConnectionError("Qdrant client not connected")
        return self.client


# Global Qdrant connection instance
qdrant_connection = QdrantConnection()


def get_qdrant() -> QdrantClient:
    """Dependency to get Qdrant client."""
    return qdrant_connection.get_client()

