# 🗄️ MongoDB Service for Location App
# File Location: backend/apps/location/mongodb_service.py

from hmip_backend.mongodb import get_collection
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class LocationMongoService:
    """Service for storing and retrieving location data from MongoDB"""

    def __init__(self):
        self.location_collection = get_collection('location_data')
        self.history_collection = get_collection('location_history')

    def store_location(self, user_id, latitude, longitude, accuracy=None, metadata=None):
        """
        Store location data in MongoDB

        Args:
            user_id: User ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            accuracy: GPS accuracy in meters
            metadata: Additional metadata dict

        Returns:
            str: Inserted document ID
        """
        try:
            document = {
                'user_id': user_id,
                'latitude': float(latitude),
                'longitude': float(longitude),
                'accuracy': float(accuracy) if accuracy else None,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }

            result = self.location_collection.insert_one(document)
            logger.info(f"Stored location for user {user_id} in MongoDB")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"❌ Failed to store location: {e}")
            raise

    def get_user_locations(self, user_id, limit=100):
        """
        Get recent locations for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            list: List of location documents
        """
        try:
            locations = list(
                self.location_collection
                .find({'user_id': user_id})
                .sort('timestamp', -1)
                .limit(limit)
            )

            # Convert ObjectId to string for JSON serialization
            for loc in locations:
                loc['_id'] = str(loc['_id'])

            return locations

        except Exception as e:
            logger.error(f"❌ Failed to get locations: {e}")
            return []

    def get_location_history(self, user_id, start_date=None, end_date=None):
        """
        Get location history for a user within a date range

        Args:
            user_id: User ID
            start_date: Start datetime
            end_date: End datetime

        Returns:
            list: List of location history documents
        """
        try:
            query = {'user_id': user_id}

            if start_date or end_date:
                query['timestamp'] = {}
                if start_date:
                    query['timestamp']['$gte'] = start_date
                if end_date:
                    query['timestamp']['$lte'] = end_date

            history = list(
                self.location_collection
                .find(query)
                .sort('timestamp', -1)
            )

            # Convert ObjectId to string
            for item in history:
                item['_id'] = str(item['_id'])

            return history

        except Exception as e:
            logger.error(f"❌ Failed to get location history: {e}")
            return []

    def delete_old_locations(self, days=30):
        """
        Delete location data older than specified days

        Args:
            days: Number of days to keep

        Returns:
            int: Number of deleted documents
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            result = self.location_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })

            logger.info(f"🗑️ Deleted {result.deleted_count} old location records")
            return result.deleted_count

        except Exception as e:
            logger.error(f"❌ Failed to delete old locations: {e}")
            return 0

    def get_latest_location(self, user_id):
        """
        Get the most recent location for a user

        Args:
            user_id: User ID

        Returns:
            dict: Latest location document or None
        """
        try:
            location = self.location_collection.find_one(
                {'user_id': user_id},
                sort=[('timestamp', -1)]
            )

            if location:
                location['_id'] = str(location['_id'])

            return location

        except Exception as e:
            logger.error(f"❌ Failed to get latest location: {e}")
            return None

    def count_user_locations(self, user_id):
        """
        Count total locations stored for a user

        Args:
            user_id: User ID

        Returns:
            int: Number of location records
        """
        try:
            count = self.location_collection.count_documents({'user_id': user_id})
            return count

        except Exception as e:
            logger.error(f"❌ Failed to count locations: {e}")
            return 0


# Global service instance
location_mongo_service = LocationMongoService()
