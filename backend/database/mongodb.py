"""MongoDB database connection and operations."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from backend.core.config import settings


class MongoDBConnection:
    """Manages MongoDB connection and operations."""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
    
    async def connect(self):
        """Connect to MongoDB database."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.database = self.client[settings.mongodb_db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
            
        except Exception as error:
            logger.error(f"Failed to connect to MongoDB: {error}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB database."""
        if self.client is not None:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self.database is None:
            raise ConnectionError("Database not connected")
        return self.database


# Global MongoDB connection instance
mongodb_connection = MongoDBConnection()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """Dependency to get MongoDB database."""
    return mongodb_connection.get_database()

