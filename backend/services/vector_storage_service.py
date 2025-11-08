"""Vector storage service for Qdrant operations."""

from typing import List, Dict
from datetime import datetime
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from loguru import logger
from backend.database.qdrant_client import qdrant_connection
from backend.services.embedding_service import embedding_service
from backend.core.config import settings


class VectorStorageService:
    """Handles vector storage operations with Qdrant."""
    
    def __init__(self):
        self.collection_name = "research_documents"
    
    async def store_document_chunks(
        self, 
        document_id: str,
        chunks: List[str],
        metadata: Dict[str, str]
    ) -> List[str]:
        """
        Store document chunks as vectors in Qdrant.
        
        Args:
            document_id: Unique identifier for the document
            chunks: List of text chunks to store
            metadata: Document metadata
            
        Returns:
            List of point IDs created in Qdrant
        """
        try:
            if not chunks:
                logger.warning(f"No chunks to store for document: {document_id}")
                return []
            
            # Generate embeddings for all chunks
            embeddings = await embedding_service.create_embeddings_batch(chunks)
            
            # Prepare points for Qdrant
            points = []
            point_ids = []
            
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = f"{document_id}_chunk_{index}"
                point_ids.append(point_id)
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "chunk_index": index,
                        "text": chunk,
                        "user_id": metadata.get("user_id", settings.user_id),
                        "file_name": metadata.get("file_name", ""),
                        "file_type": metadata.get("file_type", ""),
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                
                points.append(point)
            
            # Store in Qdrant
            client = qdrant_connection.get_client()
            
            client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Stored {len(points)} chunks for document: {document_id}")
            return point_ids
            
        except Exception as error:
            logger.error(f"Failed to store document chunks: {error}")
            raise
    
    async def search_similar_chunks(
        self, 
        query: str, 
        limit: int = 5,
        user_id: str = None,
        document_id: str = None
    ) -> List[Dict[str, str]]:
        """
        Search for similar chunks using semantic search.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            user_id: Filter by user ID
            document_id: Filter by specific document
            
        Returns:
            List of similar chunks with scores
        """
        try:
            # Generate query embedding
            query_embedding = await embedding_service.create_embedding(query)
            
            # Build filter
            filter_conditions = []
            
            if user_id:
                filter_conditions.append(
                    FieldCondition(key="user_id", match=MatchValue(value=user_id))
                )
            
            if document_id:
                filter_conditions.append(
                    FieldCondition(key="document_id", match=MatchValue(value=document_id))
                )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Search in Qdrant
            client = qdrant_connection.get_client()
            
            search_results = client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": str(result.id),
                    "text": result.payload["text"],
                    "score": str(result.score),
                    "document_id": result.payload["document_id"],
                    "file_name": result.payload["file_name"],
                    "chunk_index": str(result.payload["chunk_index"])
                })
            
            logger.info(f"Found {len(results)} similar chunks for query: {query}")
            return results
            
        except Exception as error:
            logger.error(f"Failed to search similar chunks: {error}")
            raise
    
    async def delete_document_vectors(self, document_id: str) -> bool:
        """
        Delete all vectors associated with a document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if successful
        """
        try:
            client = qdrant_connection.get_client()
            
            # Delete points with matching document_id
            client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(key="document_id", match=MatchValue(value=document_id))
                    ]
                )
            )
            
            logger.info(f"Deleted vectors for document: {document_id}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to delete document vectors: {error}")
            raise
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, str]]:
        """
        Retrieve all chunks for a specific document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of document chunks
        """
        try:
            client = qdrant_connection.get_client()
            
            # Scroll through all points with matching document_id
            scroll_result = client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="document_id", match=MatchValue(value=document_id))
                    ]
                ),
                limit=100
            )
            
            points = scroll_result[0]
            
            chunks = []
            for point in points:
                chunks.append({
                    "id": str(point.id),
                    "text": point.payload["text"],
                    "chunk_index": str(point.payload["chunk_index"]),
                    "file_name": point.payload["file_name"]
                })
            
            # Sort by chunk index
            chunks.sort(key=lambda x: int(x["chunk_index"]))
            
            logger.info(f"Retrieved {len(chunks)} chunks for document: {document_id}")
            return chunks
            
        except Exception as error:
            logger.error(f"Failed to get document chunks: {error}")
            raise


# Global vector storage service instance
vector_storage_service = VectorStorageService()

