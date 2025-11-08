"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from backend.database.mongodb import mongodb_connection
from backend.database.qdrant_client import qdrant_connection
from backend.services.embedding_service import embedding_service
from backend.services.llm_service import gemini_service
from backend.api.routes import health, documents, search


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting Research Assistant backend...")
    
    try:
        # Connect to MongoDB
        await mongodb_connection.connect()
        
        # Connect to Qdrant
        qdrant_connection.connect()
        qdrant_connection.create_collection_if_not_exists(
            vector_size=embedding_service.get_vector_size()
        )
        
        # Load embedding model
        embedding_service.load_model()
        
        # Initialize Gemini
        gemini_service.initialize()
        
        logger.info("All services initialized successfully")
        
    except Exception as error:
        logger.error(f"Failed to initialize services: {error}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Research Assistant backend...")
    await mongodb_connection.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Intelligent Research Assistant API",
    description="Multi-agent research assistant with RAG capabilities",
    version="1.0.0",
    lifespan=app_lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(search.router, tags=["Search"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Intelligent Research Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

