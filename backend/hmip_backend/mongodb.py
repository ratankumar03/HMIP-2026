# 🗄️ MongoDB Connection Manager
# File Location: backend/hmip_backend/mongodb.py

from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """
    Singleton MongoDB connection manager
    """
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self.connect()

    def connect(self):
        """Establish connection to MongoDB"""
        try:
            mongo_host = getattr(settings, 'MONGO_HOST', 'localhost')
            mongo_port = getattr(settings, 'MONGO_PORT', 27017)
            mongo_db_name = getattr(settings, 'MONGO_DB_NAME', 'hmip_db')
            mongo_user = getattr(settings, 'MONGO_USER', '')
            mongo_password = getattr(settings, 'MONGO_PASSWORD', '')

            # Build connection string
            if mongo_user and mongo_password:
                connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
            else:
                connection_string = f"mongodb://{mongo_host}:{mongo_port}/"

            # Create MongoDB client
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )

            # Test connection
            self._client.server_info()

            # Get database
            self._db = self._client[mongo_db_name]

            logger.info(f"Connected to MongoDB: {mongo_db_name} at {mongo_host}:{mongo_port}")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @property
    def client(self):
        """Get MongoDB client"""
        if self._client is None:
            self.connect()
        return self._client

    @property
    def db(self):
        """Get MongoDB database"""
        if self._db is None:
            self.connect()
        return self._db

    def get_collection(self, collection_name):
        """Get a MongoDB collection"""
        return self.db[collection_name]

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")


# Global MongoDB instance
mongodb = MongoDBConnection()


def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb.db


def get_collection(name):
    """Get a MongoDB collection by name"""
    return mongodb.get_collection(name)
