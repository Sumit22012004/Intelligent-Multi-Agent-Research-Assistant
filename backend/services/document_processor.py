"""Document processing service for PDFs and images."""

from pathlib import Path
from typing import Dict
from pypdf import PdfReader
from PIL import Image
from loguru import logger
from backend.services.llm_service import gemini_service

class DocumentProcessor:
    """Handles document processing for PDFs and images."""
    
    def __init__(self):
        self.supported_image_formats = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        self.supported_document_formats = [".pdf"]
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported."""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_image_formats + self.supported_document_formats
    
    def get_file_type(self, file_path: str) -> str:
        """Determine file type (image or pdf)."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension in self.supported_image_formats:
            return "image"
        elif file_extension in self.supported_document_formats:
            return "pdf"
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF using PyPDF."""
        try:
            pdf_reader = PdfReader(pdf_path)
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            logger.info(f"Extracted text from PDF: {pdf_path} ({len(pdf_reader.pages)} pages)")
            return text_content.strip()
            
        except Exception as error:
            logger.error(f"Failed to extract text from PDF: {error}")
            raise
    
    async def analyze_pdf_with_vision(self, pdf_path: str, prompt: str) -> str:
        """Analyze PDF using Gemini Vision for complex layouts."""
        try:
            response = await gemini_service.analyze_pdf(pdf_path, prompt)
            logger.info(f"Analyzed PDF with vision: {pdf_path}")
            return response
            
        except Exception as error:
            logger.error(f"Failed to analyze PDF with vision: {error}")
            raise
    
    async def analyze_image_with_vision(self, image_path: str, prompt: str) -> str:
        """Analyze image using Gemini Vision."""
        try:
            response = await gemini_service.analyze_image(image_path, prompt)
            logger.info(f"Analyzed image: {image_path}")
            return response
            
        except Exception as error:
            logger.error(f"Failed to analyze image: {error}")
            raise
    
    def get_image_info(self, image_path: str) -> Dict[str, str]:
        """Get basic image information."""
        try:
            with Image.open(image_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": f"{img.width}x{img.height}",
                    "width": str(img.width),
                    "height": str(img.height)
                }
        except Exception as error:
            logger.error(f"Failed to get image info: {error}")
            raise
    
    async def process_document(self, file_path: str, use_vision: bool = False) -> Dict[str, str]:
        """
        Process a document (PDF or image) and extract content.
        
        Args:
            file_path: Path to the document
            use_vision: Whether to use Gemini Vision for complex analysis
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            if not self.is_supported_format(file_path):
                raise ValueError(f"Unsupported file format: {file_path}")
            
            file_type = self.get_file_type(file_path)
            file_name = Path(file_path).name
            
            result = {
                "file_name": file_name,
                "file_type": file_type,
                "file_path": file_path
            }
            
            if file_type == "pdf":
                if use_vision:
                    # Use Gemini Vision for complex PDFs
                    prompt = "Extract all text content from this PDF document. Preserve structure and formatting."
                    result["content"] = await self.analyze_pdf_with_vision(file_path, prompt)
                    result["extraction_method"] = "gemini_vision"
                else:
                    # Use PyPDF for simple text extraction
                    result["content"] = await self.extract_text_from_pdf(file_path)
                    result["extraction_method"] = "pypdf"
            
            elif file_type == "image":
                # Get image info
                image_info = self.get_image_info(file_path)
                result.update(image_info)
                
                # Use Gemini Vision to extract text/analyze image
                prompt = "Describe this image in detail and extract any text present in it."
                result["content"] = await self.analyze_image_with_vision(file_path, prompt)
                result["extraction_method"] = "gemini_vision"
            
            logger.info(f"Successfully processed document: {file_name}")
            return result
            
        except Exception as error:
            logger.error(f"Failed to process document: {error}")
            raise


# Global document processor instance
document_processor = DocumentProcessor()

