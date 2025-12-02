// MongoDB Initialization Script
db = db.getSiblingDB('hmip_db');

// Create collections
db.createCollection('users');
db.createCollection('location_data');
db.createCollection('location_permissions');
db.createCollection('safe_zones');

// Create indexes for performance
db.users.createIndex({ "phone": 1 }, { unique: true });
db.location_data.createIndex({ "user": 1, "timestamp": -1 });
db.location_data.createIndex({ "latitude": 1, "longitude": 1 });
db.location_permissions.createIndex({ "requester": 1, "status": 1 });
db.location_permissions.createIndex({ "target": 1, "status": 1 });

print("MongoDB initialization completed!");