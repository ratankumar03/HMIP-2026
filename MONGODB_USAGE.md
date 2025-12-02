# MongoDB Usage Guide for HMIP Project

## Overview

This project uses a **hybrid database approach**:
- **SQLite**: For Django's built-in models (User, Admin, Sessions, etc.)
- **MongoDB**: For application data (Locations, Permissions, Notifications, etc.)

This approach gives you the best of both worlds - Django's powerful ORM for authentication and admin, and MongoDB's flexibility for your app data.

## Architecture

### Files Structure
```
backend/
├── hmip_backend/
│   ├── mongodb.py          # MongoDB connection manager
│   └── settings.py          # MongoDB configuration
├── apps/
│   └── location/
│       └── mongodb_service.py  # Example MongoDB service
```

### MongoDB Connection

The MongoDB connection is managed by a singleton class in `backend/hmip_backend/mongodb.py`:

```python
from hmip_backend.mongodb import get_mongodb, get_collection

# Get database instance
db = get_mongodb()

# Get a specific collection
users_collection = get_collection('users')
locations_collection = get_collection('location_data')
```

## Using MongoDB in Your Views

### Example 1: Storing Location Data

```python
from apps.location.mongodb_service import location_mongo_service
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def store_location(request):
    user_id = request.user.id
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    accuracy = request.data.get('accuracy')

    # Store in MongoDB
    doc_id = location_mongo_service.store_location(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy,
        metadata={'device': request.data.get('device')}
    )

    return Response({
        'success': True,
        'document_id': doc_id
    })
```

### Example 2: Retrieving Location History

```python
@api_view(['GET'])
def get_location_history(request):
    user_id = request.user.id
    limit = int(request.query_params.get('limit', 100))

    # Get from MongoDB
    locations = location_mongo_service.get_user_locations(
        user_id=user_id,
        limit=limit
    )

    return Response({
        'count': len(locations),
        'locations': locations
    })
```

### Example 3: Direct MongoDB Operations

```python
from hmip_backend.mongodb import get_collection
from datetime import datetime

@api_view(['POST'])
def create_permission_request(request):
    permissions_collection = get_collection('permissions')

    # Insert document
    result = permissions_collection.insert_one({
        'requester_id': request.user.id,
        'target_id': request.data.get('target_id'),
        'permission_type': request.data.get('type'),
        'status': 'pending',
        'created_at': datetime.utcnow()
    })

    return Response({
        'permission_id': str(result.inserted_id)
    })
```

## Creating MongoDB Services for Other Apps

You can create similar services for other apps. Here's a template:

### Example: Permissions MongoDB Service

```python
# backend/apps/permissions/mongodb_service.py

from hmip_backend.mongodb import get_collection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PermissionsMongoService:
    def __init__(self):
        self.collection = get_collection('permissions')

    def create_permission(self, requester_id, target_id, permission_type):
        """Create a new permission request"""
        try:
            document = {
                'requester_id': requester_id,
                'target_id': target_id,
                'permission_type': permission_type,
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            result = self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create permission: {e}")
            raise

    def get_user_permissions(self, user_id):
        """Get all permissions for a user"""
        try:
            permissions = list(self.collection.find({
                '$or': [
                    {'requester_id': user_id},
                    {'target_id': user_id}
                ]
            }))
            for perm in permissions:
                perm['_id'] = str(perm['_id'])
            return permissions
        except Exception as e:
            logger.error(f"Failed to get permissions: {e}")
            return []

# Global instance
permissions_mongo_service = PermissionsMongoService()
```

## MongoDB Collections

Your database `hmip_db` will contain these collections:

| Collection Name | Purpose | Example Document |
|----------------|---------|------------------|
| `location_data` | Real-time location tracking | `{user_id: 1, latitude: 40.7128, longitude: -74.0060, timestamp: ISODate()}` |
| `location_history` | Historical location data | `{user_id: 1, locations: [...], date: ISODate()}` |
| `permissions` | Permission requests | `{requester_id: 1, target_id: 2, status: 'active', expires_at: ISODate()}` |
| `notifications` | User notifications | `{user_id: 1, type: 'alert', message: '...', read: false}` |
| `safe_zones` | User-defined safe zones | `{user_id: 1, name: 'Home', center: [lat, lng], radius: 500}` |
| `ai_predictions` | ML model predictions | `{user_id: 1, model: 'anomaly', prediction: {...}, timestamp: ISODate()}` |

## Configuration

MongoDB settings are in `.env`:

```env
MONGO_DB_NAME=hmip_db
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=
MONGO_PASSWORD=
```

## Viewing Data in MongoDB Compass

1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017`
3. Navigate to `hmip_db` database
4. Browse collections:
   - `location_data` - See stored location points
   - `permissions` - See permission requests
   - etc.

## Common MongoDB Operations

### Insert Document
```python
from hmip_backend.mongodb import get_collection

collection = get_collection('my_collection')
result = collection.insert_one({'key': 'value'})
doc_id = str(result.inserted_id)
```

### Find Documents
```python
# Find all
documents = list(collection.find({}))

# Find with filter
documents = list(collection.find({'status': 'active'}))

# Find one
document = collection.find_one({'_id': ObjectId(doc_id)})
```

### Update Document
```python
from bson import ObjectId

collection.update_one(
    {'_id': ObjectId(doc_id)},
    {'$set': {'status': 'completed'}}
)
```

### Delete Document
```python
collection.delete_one({'_id': ObjectId(doc_id)})
```

### Aggregation
```python
pipeline = [
    {'$match': {'user_id': 1}},
    {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
]
results = list(collection.aggregate(pipeline))
```

## Best Practices

1. **Always convert ObjectId to string** when returning documents to API:
   ```python
   for doc in documents:
       doc['_id'] = str(doc['_id'])
   ```

2. **Use UTC timestamps**:
   ```python
   from datetime import datetime
   timestamp = datetime.utcnow()
   ```

3. **Handle exceptions**:
   ```python
   try:
       result = collection.insert_one(document)
   except Exception as e:
       logger.error(f"MongoDB error: {e}")
       raise
   ```

4. **Use indexes** for better performance:
   ```python
   collection.create_index([('user_id', 1), ('timestamp', -1)])
   ```

5. **Keep Django models** for:
   - User authentication
   - Django admin
   - Permissions/Groups
   - Sessions

6. **Use MongoDB** for:
   - Time-series data (locations)
   - Flexible schemas
   - High-write scenarios
   - Large datasets

## Testing MongoDB Connection

```bash
cd backend
./venv/Scripts/python.exe -c "from hmip_backend.mongodb import mongodb; print(f'Connected to: {mongodb.db.name}'); print(f'Collections: {mongodb.db.list_collection_names()}')"
```

## Example: Complete CRUD API with MongoDB

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hmip_backend.mongodb import get_collection
from bson import ObjectId
from datetime import datetime

collection = get_collection('items')

@api_view(['POST'])
def create_item(request):
    document = {
        'user_id': request.user.id,
        'title': request.data.get('title'),
        'description': request.data.get('description'),
        'created_at': datetime.utcnow()
    }
    result = collection.insert_one(document)
    return Response({'id': str(result.inserted_id)})

@api_view(['GET'])
def list_items(request):
    items = list(collection.find({'user_id': request.user.id}))
    for item in items:
        item['_id'] = str(item['_id'])
    return Response(items)

@api_view(['GET'])
def get_item(request, item_id):
    item = collection.find_one({'_id': ObjectId(item_id)})
    if item:
        item['_id'] = str(item['_id'])
        return Response(item)
    return Response({'error': 'Not found'}, status=404)

@api_view(['PUT'])
def update_item(request, item_id):
    collection.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': request.data}
    )
    return Response({'success': True})

@api_view(['DELETE'])
def delete_item(request, item_id):
    collection.delete_one({'_id': ObjectId(item_id)})
    return Response({'success': True})
```

## Need Help?

- MongoDB Docs: https://docs.mongodb.com/
- PyMongo Docs: https://pymongo.readthedocs.io/
- Check logs at: `backend/logs/django.log`
