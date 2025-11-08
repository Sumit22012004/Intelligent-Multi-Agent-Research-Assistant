"""Text chunking utilities for document processing."""

from typing import List
from loguru import logger
from backend.core.config import settings


class TextChunker:
    """Handles text chunking for vector storage."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        try:
            if not text or len(text.strip()) == 0:
                return []
            
            # Clean the text
            text = text.strip()
            
            chunks = []
            start_index = 0
            
            while start_index < len(text):
                # Calculate end index for this chunk
                end_index = start_index + self.chunk_size
                
                # If this is not the last chunk, try to break at sentence boundary
                if end_index < len(text):
                    # Look for sentence endings near the chunk boundary
                    search_start = max(start_index, end_index - 100)
                    search_text = text[search_start:end_index + 100]
                    
                    # Find the last sentence ending
                    for separator in [". ", ".\n", "! ", "!\n", "? ", "?\n"]:
                        last_separator = search_text.rfind(separator)
                        if last_separator != -1:
                            end_index = search_start + last_separator + 1
                            break
                
                # Extract the chunk
                chunk = text[start_index:end_index].strip()
                
                if chunk:
                    chunks.append(chunk)
                
                # Move to next chunk with overlap
                start_index = end_index - self.chunk_overlap
                
                # Prevent infinite loop
                if start_index <= end_index - self.chunk_size:
                    start_index = end_index
            
            logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
            return chunks
            
        except Exception as error:
            logger.error(f"Failed to chunk text: {error}")
            raise
    
    def chunk_text_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into chunks by paragraphs, respecting chunk size limits.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        try:
            if not text or len(text.strip()) == 0:
                return []
            
            # Split by paragraphs
            paragraphs = text.split("\n\n")
            
            chunks = []
            current_chunk = ""
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                
                if not paragraph:
                    continue
                
                # If adding this paragraph exceeds chunk size
                if len(current_chunk) + len(paragraph) + 2 > self.chunk_size:
                    # Save current chunk if not empty
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # If paragraph itself is too large, split it
                    if len(paragraph) > self.chunk_size:
                        paragraph_chunks = self.chunk_text(paragraph)
                        chunks.extend(paragraph_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = paragraph
                else:
                    # Add paragraph to current chunk
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # Add the last chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            logger.info(f"Created {len(chunks)} chunks by paragraphs from {len(paragraphs)} paragraphs")
            return chunks
            
        except Exception as error:
            logger.error(f"Failed to chunk text by paragraphs: {error}")
            raise


# Global text chunker instance
text_chunker = TextChunker()

