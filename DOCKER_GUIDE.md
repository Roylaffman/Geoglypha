# Docker Guide for Geoglypha Flask API

This guide explains how to use Docker to run the Geoglypha Flask API locally for development and testing.

## Prerequisites

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop/
   - After installation, ensure Docker Desktop is running (check system tray)

2. **Terminal/Command Prompt** access

## Quick Start

```bash
# Navigate to project directory
cd c:\Users\royla\OneDrive\Documents\2.9Dev\Geoglypha

# Build the Docker image
docker build -t geoglypha-api .

# Run the container
docker run -d -p 5000:8080 --name geoglypha-api geoglypha-api

# Test the API
curl http://localhost:5000/
```

## Understanding the Dockerfile

The `Dockerfile` in this project:

```dockerfile
FROM python:3.9-slim                    # Base image with Python 3.9

WORKDIR /app                            # Set working directory inside container

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \                         # For file type detection
    libpq-dev \                         # For PostgreSQL support
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .                 # Copy dependencies file
RUN pip install --no-cache-dir -r requirements.txt  # Install Python packages

COPY app.py .                           # Copy application files
COPY models.py .
COPY init_db.py .

ENV PORT=8080                           # Default port
EXPOSE 8080                             # Expose port to host

# Run with gunicorn (production server)
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 app:app
```

## Common Docker Commands

### Building Images

```bash
# Build with default tag
docker build -t geoglypha-api .

# Build with version tag
docker build -t geoglypha-api:v1.0 .

# Rebuild without cache (useful after changing requirements.txt)
docker build --no-cache -t geoglypha-api .
```

### Running Containers

```bash
# Run in foreground (see logs directly)
docker run -p 5000:8080 --name geoglypha-api geoglypha-api

# Run in background (detached mode)
docker run -d -p 5000:8080 --name geoglypha-api geoglypha-api

# Run with environment variables
docker run -d -p 5000:8080 \
  -e BUCKET_NAME=geoglypha1 \
  -e DB_HOST=localhost \
  --name geoglypha-api geoglypha-api

# Run with local volume mount (for development)
docker run -d -p 5000:8080 \
  -v $(pwd)/app.py:/app/app.py \
  --name geoglypha-api geoglypha-api
```

### Managing Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop geoglypha-api

# Start a stopped container
docker start geoglypha-api

# Restart a container
docker restart geoglypha-api

# Remove a container (must be stopped first)
docker rm geoglypha-api

# Stop and remove in one command
docker rm -f geoglypha-api
```

### Viewing Logs

```bash
# View all logs
docker logs geoglypha-api

# Follow logs in real-time
docker logs -f geoglypha-api

# View last 50 lines
docker logs --tail 50 geoglypha-api
```

### Debugging

```bash
# Open a shell inside the running container
docker exec -it geoglypha-api /bin/bash

# Run a one-off command
docker exec geoglypha-api python --version

# Check container resource usage
docker stats geoglypha-api
```

### Cleanup

```bash
# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused (containers, images, networks)
docker system prune

# List images
docker images

# Remove a specific image
docker rmi geoglypha-api
```

## Port Mapping Explained

```
docker run -p 5000:8080 ...
            ↑     ↑
            │     └── Container port (where app runs inside Docker)
            └──────── Host port (where you access it on localhost)
```

- The Flask app runs on port **8080** inside the container
- We map it to port **5000** on your computer
- Access at: `http://localhost:5000/`

## Testing the API

### Test Root Endpoint
```bash
curl http://localhost:5000/
```

Expected response:
```json
{
  "service": "Geoglypha Tools API",
  "version": "1.0.0",
  "endpoints": {
    "POST /upload": "Upload KML/KMZ file, returns GeoJSON",
    "POST /download": "Download GeoJSON as file",
    "GET /api/geoglyphs": "List all geoglyph points",
    "GET /api/geoglyphs/<id>": "Get single geoglyph"
  }
}
```

### Test File Upload
```bash
# Upload a KML file
curl -X POST -F "file=@sample.kml" http://localhost:5000/upload
```

### Using PowerShell (Windows)
```powershell
# Test root endpoint
Invoke-RestMethod -Uri http://localhost:5000/

# Upload a file
$form = @{ file = Get-Item -Path "sample.kml" }
Invoke-RestMethod -Uri http://localhost:5000/upload -Method Post -Form $form
```

## Development Workflow

### 1. Make Code Changes
Edit `app.py` or other files locally.

### 2. Rebuild and Restart
```bash
# Stop and remove old container
docker rm -f geoglypha-api

# Rebuild image
docker build -t geoglypha-api .

# Start new container
docker run -d -p 5000:8080 --name geoglypha-api geoglypha-api
```

### 3. One-Liner for Quick Iteration
```bash
docker rm -f geoglypha-api; docker build -t geoglypha-api . && docker run -d -p 5000:8080 --name geoglypha-api geoglypha-api && docker logs -f geoglypha-api
```

## Troubleshooting

### "Port already in use"
```bash
# Find what's using the port
netstat -ano | findstr :5000

# Use a different port
docker run -d -p 5001:8080 --name geoglypha-api geoglypha-api
```

### "Container already exists"
```bash
# Remove the existing container
docker rm -f geoglypha-api
```

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is running
- Check the system tray for the Docker icon

### Check Container Health
```bash
# See if container is running
docker ps

# Check logs for errors
docker logs geoglypha-api
```

## Environment Variables

The Flask app supports these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port to run on | `8080` |
| `BUCKET_NAME` | GCS bucket name | (none) |
| `DB_HOST` | Database host | (none) |
| `DB_NAME` | Database name | `geoglypha` |
| `DB_USER` | Database user | `geoglypha_user` |
| `DB_PASS` | Database password | (none) |

Example with environment variables:
```bash
docker run -d -p 5000:8080 \
  -e PORT=8080 \
  -e BUCKET_NAME=geoglypha1 \
  --name geoglypha-api geoglypha-api
```

## Next Steps: Deploying to Cloud

Once tested locally, the same Docker image can be deployed to:

### Google Cloud Run
```bash
# Tag for GCR
docker tag geoglypha-api gcr.io/YOUR_PROJECT/geoglypha-api

# Push to GCR
docker push gcr.io/YOUR_PROJECT/geoglypha-api

# Deploy to Cloud Run
gcloud run deploy geoglypha-api \
  --image gcr.io/YOUR_PROJECT/geoglypha-api \
  --platform managed \
  --allow-unauthenticated
```

### AWS ECR + ECS/EC2
```bash
# Authenticate to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com

# Tag and push
docker tag geoglypha-api YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/geoglypha-api
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/geoglypha-api
```

## Useful Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Cheat Sheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf)
- [Flask with Docker](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
