"""
Initialize the database with default user and test data.
Run this script once after setting up the environment.
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.config import settings
from backend.database.models.models import User


async def initialize_database():
    """Initialize MongoDB with default user."""
    
    print("🚀 Initializing database...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_uri)
    database = client[settings.mongodb_db_name]
    
    # Create default user
    users_collection = database["users"]
    
    existing_user = await users_collection.find_one({"user_id": settings.user_id})
    
    if not existing_user:
        default_user = User(
            user_id=settings.user_id,
            username="Default User",
            created_at=datetime.now(),
            total_sessions=0,
            total_documents=0
        )
        
        await users_collection.insert_one(default_user.dict())
        print(f"✅ Created default user: {settings.user_id}")
    else:
        print(f"✅ Default user already exists: {settings.user_id}")
    
    # Create indexes for better performance
    await database["conversations"].create_index([("session_id", 1), ("timestamp", -1)])
    await database["sessions"].create_index([("user_id", 1), ("created_at", -1)])
    await database["documents"].create_index([("user_id", 1), ("session_id", 1)])
    
    print("✅ Database indexes created")
    
    # Close connection
    client.close()
    print("✅ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(initialize_database())

