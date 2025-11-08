"""Gemini AI service for LLM operations."""

from google import genai
from loguru import logger
from backend.core.config import settings


class GeminiService:
    """Handles all Gemini AI model operations."""
    
    def __init__(self):
        self.client: genai.Client = None
        self.is_initialized = False
    
    def initialize(self):
        """Initialize Gemini AI with API key."""
        try:
            self.client = genai.Client(api_key=settings.google_api_key)
            
            self.is_initialized = True
            logger.info("Gemini AI initialized successfully")
            
        except Exception as error:
            logger.error(f"Failed to initialize Gemini AI: {error}")
            raise
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text response from Gemini."""
        if self.client is None:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            response = await self.client.aio.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            return response.text
            
        except Exception as error:
            logger.error(f"Failed to generate text: {error}")
            raise
    
    async def analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze image with Gemini vision."""
        if self.client is None:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Generate response with image
            response = await self.client.aio.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[prompt, {'mime_type': 'image/jpeg', 'data': image_data}]
            )
            return response.text
            
        except Exception as error:
            logger.error(f"Failed to analyze image: {error}")
            raise
    
    async def analyze_pdf(self, pdf_path: str, prompt: str) -> str:
        """Analyze PDF with Gemini vision."""
        if self.client is None:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            # Read PDF file
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            # Generate response with PDF
            response = await self.client.aio.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[prompt, {'mime_type': 'application/pdf', 'data': pdf_data}]
            )
            return response.text
            
        except Exception as error:
            logger.error(f"Failed to analyze PDF: {error}")
            raise


# Global Gemini service instance
gemini_service = GeminiService()

