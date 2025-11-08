"""Document processing API routes."""

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from loguru import logger

from backend.core.config import settings
from backend.core.schemas import DocumentProcessingStatus, DocumentMetadata
from backend.services.document_processor import document_processor
from backend.utils.text_chunker import text_chunker
from backend.services.vector_storage_service import vector_storage_service
from backend.database.mongodb import mongodb_connection
from backend.database.models.models import Document


router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentProcessingStatus)
async def upload_document(
    file: UploadFile = File(...),
    use_vision: bool = Form(False)
):
    """
    Upload and process a document (PDF or image).
    
    Args:
        file: The file to upload
        use_vision: Whether to use Gemini Vision for processing
        
    Returns:
        Document processing status
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > settings.max_upload_size_mb:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB"
            )
        
        # Check if format is supported
        if not document_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: PDF, JPG, JPEG, PNG, GIF, WEBP"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file to uploads directory
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = Path(file.filename).suffix
        file_path = upload_dir / f"{document_id}{file_extension}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File uploaded: {file.filename} -> {file_path}")
        
        # Process document
        processed_result = await document_processor.process_document(
            str(file_path), 
            use_vision=use_vision
        )
        
        # Chunk the extracted text
        chunks = text_chunker.chunk_text(processed_result["content"])
        
        # Store chunks in vector database
        metadata = {
            "user_id": settings.user_id,
            "file_name": file.filename,
            "file_type": processed_result["file_type"]
        }
        
        point_ids = await vector_storage_service.store_document_chunks(
            document_id=document_id,
            chunks=chunks,
            metadata=metadata
        )
        
        # Save document metadata to MongoDB
        db = mongodb_connection.get_database()
        documents_collection = db["documents"]
        
        document_record = Document(
            document_id=document_id,
            user_id=settings.user_id,
            file_name=file.filename,
            file_type=processed_result["file_type"],
            file_path=str(file_path),
            file_size=str(file_size_mb),
            extraction_method=processed_result["extraction_method"],
            chunk_count=str(len(chunks)),
            vector_ids=point_ids
        )
        
        await documents_collection.insert_one(document_record.model_dump())
        
        logger.info(f"Document processed successfully: {document_id}")
        
        return DocumentProcessingStatus(
            document_id=document_id,
            file_name=file.filename,
            status="completed",
            message=f"Document processed successfully. Created {len(chunks)} chunks.",
            chunk_count=len(chunks)
        )
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Failed to upload document: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(error)}")


@router.get("/list", response_model=List[DocumentMetadata])
async def list_documents():
    """
    List all documents for the user.
    
    Returns:
        List of document metadata
    """
    try:
        db = mongodb_connection.get_database()
        documents_collection = db["documents"]
        
        documents = await documents_collection.find(
            {"user_id": settings.user_id}
        ).to_list(length=100)
        
        result = []
        for doc in documents:
            result.append(DocumentMetadata(
                document_id=doc["document_id"],
                file_name=doc["file_name"],
                file_type=doc["file_type"],
                file_size=doc["file_size"],
                chunk_count=doc["chunk_count"],
                created_at=doc["created_at"]
            ))
        
        logger.info(f"Retrieved {len(result)} documents")
        return result
        
    except Exception as error:
        logger.error(f"Failed to list documents: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(error)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its vectors.
    
    Args:
        document_id: The document ID to delete
        
    Returns:
        Success message
    """
    try:
        db = mongodb_connection.get_database()
        documents_collection = db["documents"]
        
        # Get document from MongoDB
        document = await documents_collection.find_one({"document_id": document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from disk
        file_path = Path(document["file_path"])
        if file_path.exists():
            os.remove(file_path)
        
        # Delete vectors from Qdrant
        await vector_storage_service.delete_document_vectors(document_id)
        
        # Delete from MongoDB
        await documents_collection.delete_one({"document_id": document_id})
        
        logger.info(f"Document deleted: {document_id}")
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Failed to delete document: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(error)}")


@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str):
    """
    Get all chunks for a document.
    
    Args:
        document_id: The document ID
        
    Returns:
        List of document chunks
    """
    try:
        chunks = await vector_storage_service.get_document_chunks(document_id)
        
        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "chunks": chunks
        }
        
    except Exception as error:
        logger.error(f"Failed to get document chunks: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunks: {str(error)}")

