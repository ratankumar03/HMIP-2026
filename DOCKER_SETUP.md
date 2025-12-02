# Docker Setup Guide for HMIP-2026

This guide explains how to run the HMIP application using Docker.

## Prerequisites

- Docker Desktop installed and running
- Git (optional, for version control)

## Project Structure

```
HMIP-2026/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .dockerignore
│   └── .env
├── frontend/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── nginx.conf
│   └── .dockerignore
├── docker-compose.yml (Production)
└── docker-compose.dev.yml (Development)
```

## Setup Instructions

### 1. Create Environment File

First, create a `.env` file in the backend directory:

```powershell
cp backend\.env.example backend\.env
```

Edit `backend/.env` if needed to customize settings.

### 2. Production Mode (Recommended for deployment)

Build and run all services in production mode:

```powershell
docker-compose up --build
```

This will start:
- **Redis** on port 6379
- **Backend (Django)** on port 8000
- **Celery Worker** for async tasks
- **Celery Beat** for scheduled tasks
- **Frontend (Nginx)** on port 80

Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- Backend Admin: http://localhost:8000/admin

To run in detached mode (background):
```powershell
docker-compose up -d --build
```

To stop:
```powershell
docker-compose down
```

To stop and remove volumes:
```powershell
docker-compose down -v
```

### 3. Development Mode (Hot Reload)

For development with hot reload enabled:

```powershell
docker-compose -f docker-compose.dev.yml up --build
```

This will start:
- **Redis** on port 6379
- **Backend (Django dev server)** on port 8000 with auto-reload
- **Celery Worker** for async tasks
- **Frontend (React dev server)** on port 3000 with hot reload

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### 4. Individual Service Management

#### Build and run only the backend:
```powershell
cd backend
docker build -t hmip-backend:latest .
docker run -p 8000:8000 hmip-backend:latest
```

#### Build and run only the frontend:
```powershell
cd frontend
docker build -t hmip-frontend:latest .
docker run -p 80:80 hmip-frontend:latest
```

## Useful Docker Commands

### View logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Execute commands in running containers
```powershell
# Backend - Django shell
docker exec -it hmip-backend python manage.py shell

# Backend - Create superuser
docker exec -it hmip-backend python manage.py createsuperuser

# Backend - Run migrations
docker exec -it hmip-backend python manage.py migrate

# Backend - Collect static files
docker exec -it hmip-backend python manage.py collectstatic --noinput

# Frontend - Access bash
docker exec -it hmip-frontend sh
```

### Restart services
```powershell
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### View running containers
```powershell
docker-compose ps
```

### Remove all containers and volumes
```powershell
docker-compose down -v
```

### Rebuild specific service
```powershell
docker-compose up -d --build backend
```

## Troubleshooting

### Port already in use
If you get a port conflict error:
```powershell
# Find process using the port (example for port 8000)
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

Or modify the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port from 8000 to 8001
```

### Container fails to start
Check logs:
```powershell
docker-compose logs backend
```

### Reset everything
```powershell
# Stop all containers
docker-compose down -v

# Remove all images
docker-compose rm -f

# Rebuild from scratch
docker-compose up --build
```

### Frontend can't connect to backend
Ensure the `REACT_APP_API_URL` in `docker-compose.yml` or `frontend/.env` points to the correct backend URL.

## Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## Production Considerations

When deploying to production:

1. Set `DEBUG=False` in backend/.env
2. Use a proper SECRET_KEY
3. Configure ALLOWED_HOSTS properly
4. Use a production database (PostgreSQL) instead of SQLite
5. Set up proper SSL/TLS certificates
6. Use environment-specific docker-compose files
7. Configure proper logging
8. Set up monitoring and health checks

## Additional Notes

- The frontend Dockerfile uses multi-stage builds for optimized image size
- Nginx serves the React build files and proxies API requests to the backend
- Celery worker uses `--pool=solo` for Windows compatibility
- Hot reload is enabled in development mode for both frontend and backend
