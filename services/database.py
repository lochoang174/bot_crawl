"""
Database connection and management module using PyMongo
"""

from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from config.settings import Settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB database manager with connection pooling and error handling"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._collections = {}
    
    def connect(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            # Create MongoDB client with connection pooling
            self.client = MongoClient(
                self.settings.MONGODB_CONNECTION_STRING,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                maxPoolSize=10,  # Connection pool size
                minPoolSize=1,
                maxIdleTimeMS=30000,  # 30 seconds
                retryWrites=True,
                retryReads=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database
            self.database = self.client[self.settings.MONGODB_DATABASE_NAME]
            
            logger.info(f"Successfully connected to MongoDB database: {self.settings.MONGODB_DATABASE_NAME}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get MongoDB collection by name"""
        if self.database is None:
            logger.error("Database not connected")
            return None
        
        if collection_name not in self._collections:
            self._collections[collection_name] = self.database[collection_name]
        
        return self._collections[collection_name]
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
        except:
            pass
        return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        settings = Settings()
        db_manager = DatabaseManager(settings)
    return db_manager


def init_database() -> bool:
    """Initialize database connection"""
    global db_manager
    db_manager = get_db_manager()
    return db_manager.connect()


def close_database():
    """Close database connection"""
    global db_manager
    if db_manager:
        db_manager.disconnect()
        db_manager = None 