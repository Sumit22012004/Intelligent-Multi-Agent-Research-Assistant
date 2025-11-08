"""
Download and cache HuggingFace models.
Run this before starting the application for the first time.
"""

from sentence_transformers import SentenceTransformer
from backend.core.config import settings


def download_models():
    """Download HuggingFace embedding model."""
    
    print("📥 Downloading HuggingFace models...")
    print(f"Model: {settings.hf_model_name}")
    print(f"Cache directory: {settings.hf_cache_dir}")
    
    try:
        model = SentenceTransformer(
            settings.hf_model_name,
            cache_folder=settings.hf_cache_dir
        )
        
        # Test the model
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)
        
        print("✅ Model loaded successfully")
        print(f"✅ Vector size: {len(embedding)}")
        print(f"✅ Models cached at: {settings.hf_cache_dir}")
        
    except Exception as error:
        print(f"❌ Failed to download models: {error}")
        raise


if __name__ == "__main__":
    download_models()

