# 📊 Monitoring & Logs Guide - HMIP Project

## Quick Start Monitoring Commands

### Terminal Setup (Run in separate terminals)

**Terminal 1 - Django Server:**
```bash
cd backend
./venv/Scripts/activate
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
./venv/Scripts/activate
celery -A hmip_backend worker --loglevel=info
```

**Terminal 3 - Celery Beat (Periodic Tasks):**
```bash
cd backend
./venv/Scripts/activate
celery -A hmip_backend beat --loglevel=info
```

**Terminal 4 - Redis (if not running as service):**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Terminal 5 - MongoDB (if not running as service):**
```bash
# If you have MongoDB installed locally
mongod --dbpath="C:\data\db"

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

---

## 📋 View Django Logs

### Real-time Django Server Logs
```bash
cd backend
python manage.py runserver --verbosity 2
```

**Verbosity Levels:**
- `0` - Minimal output
- `1` - Normal output (default)
- `2` - Verbose output
- `3` - Very verbose output

### View Application Logs
```bash
# View all logs
type backend\logs\django.log

# View last 50 lines
powershell -Command "Get-Content backend\logs\django.log -Tail 50"

# Monitor logs in real-time (PowerShell)
powershell -Command "Get-Content backend\logs\django.log -Wait -Tail 50"
```

### Filter Logs by Level
```bash
# Show only errors
findstr /C:"[ERROR]" backend\logs\django.log

# Show only warnings
findstr /C:"[WARNING]" backend\logs\django.log

# Show INFO logs
findstr /C:"[INFO]" backend\logs\django.log
```

---

## 🔄 View Celery Logs

### Celery Worker Logs (Verbose)
```bash
cd backend
celery -A hmip_backend worker --loglevel=debug
```

**Log Levels:**
- `debug` - Very detailed logs
- `info` - General information
- `warning` - Warning messages only
- `error` - Error messages only
- `critical` - Critical errors only

### Celery Beat Logs
```bash
cd backend
celery -A hmip_backend beat --loglevel=info
```

### Monitor Celery Tasks
```bash
# Start Celery Flower (Web-based monitoring)
cd backend
./venv/Scripts/pip install flower
celery -A hmip_backend flower

# Access at: http://localhost:5555
```

### Celery Task Status
```python
# In Django shell
python manage.py shell

from apps.authentication.tasks import send_otp_email

# Queue a task
result = send_otp_email.delay('user@example.com', '123456')

# Check task status
print(result.state)  # PENDING, SUCCESS, FAILURE
print(result.result)  # Task result
```

---

## 🗄️ MongoDB Monitoring

### MongoDB Shell (mongosh)
```bash
# Connect to MongoDB
mongosh

# Or with explicit connection
mongosh mongodb://localhost:27017
```

### MongoDB Commands

**Basic Database Operations:**
```javascript
// Show all databases
show dbs

// Switch to HMIP database
use hmip_db

// Show all collections
show collections

// Get database stats
db.stats()
```

**Query Location Data:**
```javascript
// Count total locations
db.location_data.countDocuments()

// View latest 10 locations
db.location_data.find().sort({timestamp: -1}).limit(10)

// Find locations for specific user
db.location_data.find({user_id: 1}).pretty()

// Find locations in last hour
db.location_data.find({
  timestamp: {
    $gte: new Date(Date.now() - 3600000)
  }
}).pretty()

// Count locations by user
db.location_data.aggregate([
  {$group: {_id: "$user_id", count: {$sum: 1}}},
  {$sort: {count: -1}}
])
```

**Query Other Collections:**
```javascript
// Permissions
db.permissions.find({status: 'active'}).pretty()

// Notifications
db.notifications.find({user_id: 1, read: false}).pretty()

// Safe Zones
db.safe_zones.find({user_id: 1}).pretty()
```

**Performance Monitoring:**
```javascript
// Current operations
db.currentOp()

// Server status
db.serverStatus()

// Collection statistics
db.location_data.stats()

// Index information
db.location_data.getIndexes()
```

**Create Useful Indexes:**
```javascript
// Index on user_id and timestamp for fast queries
db.location_data.createIndex({user_id: 1, timestamp: -1})

// Index on timestamp for cleanup operations
db.location_data.createIndex({timestamp: 1})

// Index on user_id for permissions
db.permissions.createIndex({user_id: 1, status: 1})
```

### MongoDB Compass (GUI)

1. **Open MongoDB Compass**
2. **Connect to**: `mongodb://localhost:27017`
3. **Select Database**: `hmip_db`
4. **Browse Collections**:
   - `location_data` - Real-time location tracking
   - `permissions` - User permissions
   - `notifications` - User notifications
   - `safe_zones` - Geofence zones

---

## 📊 System Health Checks

### Django Health Check
```bash
cd backend
python manage.py check
python manage.py check --deploy  # Production readiness
```

### Database Connection Test
```bash
cd backend
python -c "from hmip_backend.mongodb import mongodb; print(f'MongoDB: {mongodb.db.name}'); print('Collections:', mongodb.db.list_collection_names())"
```

### Redis Connection Test
```bash
cd backend
python -c "from redis import Redis; r = Redis(host='localhost', port=6379); print('Redis:', r.ping())"
```

### All Services Status Script
```python
# Create: backend/check_services.py

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hmip_backend.settings')

import django
django.setup()

from hmip_backend.mongodb import mongodb
from redis import Redis
from django.db import connection

print("=== HMIP Services Status ===\n")

# Check Django DB
try:
    connection.ensure_connection()
    print("✓ SQLite Database: Connected")
except Exception as e:
    print(f"✗ SQLite Database: {e}")

# Check MongoDB
try:
    mongodb.client.server_info()
    print(f"✓ MongoDB: Connected to '{mongodb.db.name}'")
    print(f"  Collections: {len(mongodb.db.list_collection_names())}")
except Exception as e:
    print(f"✗ MongoDB: {e}")

# Check Redis
try:
    redis_client = Redis(host='localhost', port=6379)
    redis_client.ping()
    print("✓ Redis: Connected")
    print(f"  Keys: {redis_client.dbsize()}")
except Exception as e:
    print(f"✗ Redis: {e}")

print("\n=== Services Check Complete ===")
```

Run with:
```bash
cd backend
python check_services.py
```

---

## 📈 Performance Monitoring

### Django Debug Toolbar (Development)
```bash
# Install
cd backend
./venv/Scripts/pip install django-debug-toolbar

# Add to settings.py INSTALLED_APPS:
# 'debug_toolbar',

# Add to settings.py MIDDLEWARE:
# 'debug_toolbar.middleware.DebugToolbarMiddleware',

# Add to urls.py:
# from django.conf import settings
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
```

### Monitor Database Queries
```python
# In Django shell
from django.db import connection
from django.test.utils import override_settings

# Enable query logging
with override_settings(DEBUG=True):
    # Your code here
    from apps.authentication.models import User
    users = User.objects.all()

    # View queries
    print(connection.queries)
```

### Monitor MongoDB Operations
```javascript
// Enable profiling in MongoDB
use hmip_db
db.setProfilingLevel(2)  // Log all operations

// View slow queries
db.system.profile.find({millis: {$gt: 100}}).sort({millis: -1})

// Disable profiling
db.setProfilingLevel(0)
```

---

## 🚨 Error Tracking

### View Django Errors
```bash
# View error logs
findstr /C:"[ERROR]" backend\logs\django.log

# View tracebacks
findstr /C:"Traceback" backend\logs\django.log
```

### View Celery Errors
```bash
# In Celery worker terminal, look for:
# [ERROR/ForkPoolWorker-X]
# Task ... raised unexpected: ...
```

### Common Issues & Solutions

**MongoDB Connection Error:**
```
Error: Failed to connect to MongoDB
Solution: Ensure MongoDB is running (mongod or Docker)
```

**Redis Connection Error:**
```
Error: Error 10061 connecting to localhost:6379
Solution: Start Redis server or Docker container
```

**Celery Worker Not Processing:**
```
Error: Tasks stuck in PENDING state
Solution:
1. Check Redis is running
2. Restart Celery worker
3. Check CELERY_BROKER_URL in .env
```

---

## 📦 Production Monitoring

### Using Sentry (Error Tracking)
```bash
pip install sentry-sdk

# In settings.py:
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Using Prometheus + Grafana
```bash
# Install exporters
pip install django-prometheus
pip install celery-prometheus-exporter

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django_prometheus',
    ...
]
```

### MongoDB Metrics
```javascript
// In mongo shell
db.serverStatus().metrics

// Watch operations
watch -n 1 'echo "db.serverStatus().opcounters" | mongo --quiet'
```

---

## 🔍 Useful Monitoring Queries

### Find Active Users
```python
# Django shell
from apps.authentication.models import User
from django.utils import timezone
from datetime import timedelta

active_users = User.objects.filter(
    last_login__gte=timezone.now() - timedelta(days=7)
)
print(f"Active users (7 days): {active_users.count()}")
```

### Location Data Statistics
```javascript
// MongoDB shell
use hmip_db

// Total locations stored
db.location_data.countDocuments()

// Locations by date
db.location_data.aggregate([
  {
    $group: {
      _id: {$dateToString: {format: "%Y-%m-%d", date: "$timestamp"}},
      count: {$sum: 1}
    }
  },
  {$sort: {_id: -1}},
  {$limit: 7}
])

// Average locations per user
db.location_data.aggregate([
  {$group: {_id: "$user_id", count: {$sum: 1}}},
  {$group: {_id: null, avg: {$avg: "$count"}}}
])
```

### Celery Task Statistics
```bash
# Using Celery Flower
celery -A hmip_backend flower

# Access dashboard at http://localhost:5555
# - View active/scheduled/succeeded/failed tasks
# - Monitor worker status
# - View task execution times
```

---

## 📝 Log Rotation

### Windows Log Rotation Script
```powershell
# Create: scripts/rotate_logs.ps1

$LogFile = "backend\logs\django.log"
$MaxSize = 10MB

if ((Get-Item $LogFile).length -gt $MaxSize) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $archiveFile = "backend\logs\django_$timestamp.log"
    Move-Item $LogFile $archiveFile
    Write-Host "Log rotated: $archiveFile"
}
```

Run daily:
```bash
powershell -File scripts\rotate_logs.ps1
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start Django | `python manage.py runserver` |
| Start Celery | `celery -A hmip_backend worker -l info` |
| Django Shell | `python manage.py shell` |
| MongoDB Shell | `mongosh` |
| View Logs | `type backend\logs\django.log` |
| Check Services | `python check_services.py` |
| Monitor Celery | `celery -A hmip_backend flower` |
| Database Stats | `db.stats()` in mongosh |

---

## 📞 Support

For monitoring issues:
1. Check service status with `check_services.py`
2. Review logs in `backend/logs/django.log`
3. Verify MongoDB in Compass
4. Check Celery in Flower dashboard
