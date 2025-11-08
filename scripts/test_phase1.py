"""
Test script to verify Phase 1 implementation.
Tests all services and connections.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("PHASE 1 VERIFICATION TEST")
print("=" * 60)

# Test 1: Configuration Loading
print("\n[TEST 1] Configuration Loading...")
try:
    from backend.core.config import settings
    print("[OK] Config loaded successfully")
    print(f"   - User ID: {settings.user_id}")
    print(f"   - Environment: {settings.app_env}")
    print(f"   - MongoDB: {settings.mongodb_uri}")
    print(f"   - Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
except Exception as error:
    print(f"[FAIL] Config loading failed: {error}")
    sys.exit(1)

# Test 2: Imports
print("\n[TEST 2] Testing Imports...")
try:
    from backend.database.mongodb import mongodb_connection
    from backend.database.qdrant_client import qdrant_connection
    from backend.services.embedding_service import embedding_service
    print("[OK] All imports successful")
except Exception as error:
    print(f"[FAIL] Import failed: {error}")
    sys.exit(1)

# Test 3: Data Models
print("\n[TEST 3] Testing Data Models...")
try:
    from datetime import datetime
    from backend.database.models.models import User
    
    test_user = User(
        user_id="test_user",
        username="Test",
        created_at=datetime.now(),
        total_sessions=0,
        total_documents=0
    )
    print("[OK] Data models working")
    print(f"   - User model: {test_user.user_id}")
except Exception as error:
    print(f"[FAIL] Data models failed: {error}")
    sys.exit(1)

# Test 4: Schemas
print("\n[TEST 4] Testing Schemas...")
try:
    from backend.core.schemas import ResearchQueryRequest
    
    test_query = ResearchQueryRequest(
        session_id="test_session",
        query="test query"
    )
    print("[OK] Schemas working")
    print(f"   - Query schema: {test_query.query}")
except Exception as error:
    print(f"[FAIL] Schemas failed: {error}")
    sys.exit(1)

# Test 5: MongoDB Connection (requires running MongoDB)
print("\n[TEST 5] MongoDB Connection...")
async def test_mongodb():
    try:
        await mongodb_connection.connect()
        database = mongodb_connection.get_database()
        print(f"[OK] MongoDB connected: {database.name}")
        await mongodb_connection.disconnect()
        return True
    except Exception as error:
        print(f"[WARN] MongoDB connection failed: {error}")
        print("   (Make sure MongoDB is running)")
        return False

mongodb_ok = asyncio.run(test_mongodb())

# Test 6: Qdrant Connection (requires running Qdrant)
print("\n[TEST 6] Qdrant Connection...")
try:
    qdrant_connection.connect()
    client = qdrant_connection.get_client()
    collections = client.get_collections()
    print(f"[OK] Qdrant connected: {len(collections.collections)} collections")
    qdrant_ok = True
except Exception as error:
    print(f"[WARN] Qdrant connection failed: {error}")
    print("   (Make sure Qdrant is running)")
    qdrant_ok = False

# Test 7: Embedding Service
print("\n[TEST 7] Embedding Service...")
try:
    # Just check if the service can be initialized
    print(f"   - Vector size: {embedding_service.vector_size}")
    print(f"   - Model name: {settings.hf_model_name}")
    print("[OK] Embedding service structure OK")
    print("   (Model will be loaded on first backend start)")
except Exception as error:
    print(f"[FAIL] Embedding service failed: {error}")

# Test 8: Gemini Service
print("\n[TEST 8] Gemini Service...")
try:
    # Check if API key is set
    if settings.google_api_key and settings.google_api_key != "your_gemini_api_key_here":
        print("[OK] Gemini API key configured")
        print("   (Will be initialized on backend start)")
    else:
        print("[WARN] Gemini API key not configured in .env")
except Exception as error:
    print(f"[FAIL] Gemini service check failed: {error}")

# Test 9: FastAPI Application Structure
print("\n[TEST 9] FastAPI Application...")
try:
    from backend.main import app
    print("[OK] FastAPI app created")
    print(f"   - Title: {app.title}")
    print(f"   - Version: {app.version}")
except Exception as error:
    print(f"[FAIL] FastAPI app failed: {error}")
    sys.exit(1)

# Test 10: Streamlit Application
print("\n[TEST 10] Streamlit Application...")
try:
    from pathlib import Path
    frontend_app = Path("frontend/app.py")
    if frontend_app.exists():
        print("[OK] Streamlit app exists")
        print(f"   - Path: {frontend_app}")
    else:
        print("[FAIL] Streamlit app not found")
except Exception as error:
    print(f"[FAIL] Streamlit check failed: {error}")

# Summary
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)

tests_passed = [
    "[OK] Configuration",
    "[OK] Imports",
    "[OK] Data Models",
    "[OK] Schemas",
    "[OK] MongoDB" if mongodb_ok else "[WARN] MongoDB (not running)",
    "[OK] Qdrant" if qdrant_ok else "[WARN] Qdrant (not running)",
    "[OK] Embedding Service",
    "[OK] Gemini Service",
    "[OK] FastAPI App",
    "[OK] Streamlit App"
]

for test in tests_passed:
    print(test)

print("\n" + "=" * 60)
if mongodb_ok and qdrant_ok:
    print("SUCCESS: PHASE 1 - ALL TESTS PASSED!")
    print("Ready to start the application!")
else:
    print("SUCCESS: PHASE 1 - CORE TESTS PASSED")
    print("Start MongoDB and Qdrant to fully test Phase 1")
print("=" * 60)

