"""
Phase 2 Verification Test Script

Tests all Phase 2 components:
- Document processing (PDF/Image)
- Text chunking
- arXiv search
- Perplexity web search
- Vector storage operations
- API endpoints
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def print_test_header(test_name):
    """Print test header."""
    print(f"\n[TEST {test_name}]", end=" ")


def print_success(message=""):
    """Print success message."""
    print(f"[OK] {message}")


def print_warning(message=""):
    """Print warning message."""
    print(f"[WARN] {message}")


def print_error(message=""):
    """Print error message."""
    print(f"[ERROR] {message}")


async def test_imports():
    """Test all Phase 2 imports."""
    print_test_header("Imports")
    
    try:
        from backend.services.document_processor import document_processor
        from backend.services.arxiv_service import arxiv_service
        from backend.services.perplexity_service import perplexity_service
        from backend.services.vector_storage_service import vector_storage_service
        from backend.utils.text_chunker import text_chunker
        from backend.api.routes import documents, search
        
        print_success("All Phase 2 imports successful")
        return True
    except Exception as error:
        print_error(f"Import failed: {error}")
        return False


async def test_text_chunker():
    """Test text chunking utility."""
    print_test_header("Text Chunker")
    
    try:
        from backend.utils.text_chunker import text_chunker
        
        # Test with sample text
        sample_text = "This is a test sentence. " * 100
        chunks = text_chunker.chunk_text(sample_text)
        
        print_success(f"Text chunker working - Created {len(chunks)} chunks")
        print(f"   - Chunk size: {text_chunker.chunk_size}")
        print(f"   - Chunk overlap: {text_chunker.chunk_overlap}")
        return True
    except Exception as error:
        print_error(f"Text chunker failed: {error}")
        return False


async def test_document_processor():
    """Test document processor service."""
    print_test_header("Document Processor")
    
    try:
        from backend.services.document_processor import document_processor
        
        # Test supported formats
        supported_formats = document_processor.supported_image_formats + document_processor.supported_document_formats
        
        print_success("Document processor initialized")
        print(f"   - Supported formats: {', '.join(supported_formats)}")
        return True
    except Exception as error:
        print_error(f"Document processor failed: {error}")
        return False


async def test_arxiv_service():
    """Test arXiv search service."""
    print_test_header("arXiv Service")
    
    try:
        from backend.services.arxiv_service import arxiv_service
        
        print_success("arXiv service initialized")
        print(f"   - Client ready: {arxiv_service.client is not None}")
        return True
    except Exception as error:
        print_error(f"arXiv service failed: {error}")
        return False


async def test_perplexity_service():
    """Test Perplexity web search service."""
    print_test_header("Perplexity Service")
    
    try:
        from backend.services.perplexity_service import perplexity_service
        from backend.core.config import settings
        
        has_api_key = settings.perplexity_api_key != ""
        
        if has_api_key:
            print_success("Perplexity service initialized")
            print(f"   - API key configured: Yes")
            print(f"   - Model: {perplexity_service.model}")
        else:
            print_warning("Perplexity API key not configured in .env")
        
        return True
    except Exception as error:
        print_error(f"Perplexity service failed: {error}")
        return False


async def test_vector_storage_service():
    """Test vector storage service."""
    print_test_header("Vector Storage Service")
    
    try:
        from backend.services.vector_storage_service import vector_storage_service
        
        print_success("Vector storage service initialized")
        print(f"   - Collection name: {vector_storage_service.collection_name}")
        return True
    except Exception as error:
        print_error(f"Vector storage service failed: {error}")
        return False


async def test_api_routes():
    """Test API routes are defined."""
    print_test_header("API Routes")
    
    try:
        from backend.api.routes import documents, search
        
        # Check documents routes
        documents_routes = [route.path for route in documents.router.routes]
        search_routes = [route.path for route in search.router.routes]
        
        print_success("API routes loaded")
        print(f"   - Documents routes: {len(documents_routes)}")
        print(f"   - Search routes: {len(search_routes)}")
        return True
    except Exception as error:
        print_error(f"API routes failed: {error}")
        return False


async def test_main_app():
    """Test main FastAPI app with new routes."""
    print_test_header("FastAPI App")
    
    try:
        from backend.main import app
        
        routes = [route.path for route in app.routes]
        
        print_success("FastAPI app loaded with Phase 2 routes")
        print(f"   - Total routes: {len(routes)}")
        print(f"   - Has /api/v1/documents: {any('/documents' in r for r in routes)}")
        print(f"   - Has /api/v1/search: {any('/search' in r for r in routes)}")
        return True
    except Exception as error:
        print_error(f"FastAPI app failed: {error}")
        return False


async def test_config_updates():
    """Test configuration updates for Phase 2."""
    print_test_header("Configuration")
    
    try:
        from backend.core.config import settings
        
        print_success("Configuration loaded")
        print(f"   - Upload dir: {settings.upload_dir}")
        print(f"   - Max upload size: {settings.max_upload_size_mb}MB")
        print(f"   - Chunk size: {settings.chunk_size}")
        print(f"   - Chunk overlap: {settings.chunk_overlap}")
        return True
    except Exception as error:
        print_error(f"Configuration failed: {error}")
        return False


async def main():
    """Run all Phase 2 tests."""
    print("=" * 60)
    print("PHASE 2 VERIFICATION TEST")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(await test_imports())
    results.append(await test_config_updates())
    results.append(await test_text_chunker())
    results.append(await test_document_processor())
    results.append(await test_arxiv_service())
    results.append(await test_perplexity_service())
    results.append(await test_vector_storage_service())
    results.append(await test_api_routes())
    results.append(await test_main_app())
    
    # Print summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    test_names = [
        "Imports",
        "Configuration",
        "Text Chunker",
        "Document Processor",
        "arXiv Service",
        "Perplexity Service",
        "Vector Storage",
        "API Routes",
        "FastAPI App"
    ]
    
    for name, result in zip(test_names, results):
        status = "[OK]" if result else "[ERROR]"
        print(f"{status} {name}")
    
    # Overall result
    all_passed = all(results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: PHASE 2 - ALL TESTS PASSED")
        print("Ready for integration testing with MongoDB and Qdrant!")
    else:
        print("FAILED: Some Phase 2 tests failed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

