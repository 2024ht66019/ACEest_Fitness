# 🐳 Docker Deployment Guide

Complete guide for containerizing and deploying the ACEest Fitness & Gym Management System using Docker and Docker Compose.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Services](#services)
- [Commands](#commands)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Prerequisites

Ensure you have the following installed:

- **Docker**: v20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: v2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- **Git**: For cloning the repository

Verify installations:
```bash
docker --version
docker-compose --version
```

---

## Architecture Overview

The application uses a multi-container architecture:

```
┌─────────────────────────────────────────────┐
│           Nginx (Port 80/443)               │
│          Reverse Proxy & SSL                │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│       Flask App (Port 5000)                 │
│   - Gunicorn with 4 workers                 │
│   - Python 3.13                             │
│   - Health checks enabled                   │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│      PostgreSQL 16 (Port 5432)              │
│   - Persistent volume storage               │
│   - Automatic initialization                │
└─────────────────────────────────────────────┘
```

### Components

1. **Web Service** (`web`): Flask application with Gunicorn
2. **Database Service** (`db`): PostgreSQL 16 with persistent storage
3. **Nginx Service** (`nginx`): Reverse proxy with SSL support (optional)

---

## Quick Start

### 1. Clone and Navigate

```bash
cd /home/dharmalakshmi15/Projects/bits_pilani-Devops_assignment/flask_app
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
nano .env
```

**Important**: Change these values:
- `SECRET_KEY`: Generate a secure random key
- `POSTGRES_PASSWORD`: Use a strong password

### 3. Build and Start Services

```bash
# Build images and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### 4. Access Application

- **Application**: http://localhost:5000
- **Through Nginx**: http://localhost:80
- **Database**: localhost:5432 (if needed)

### 5. Create Test User (Optional)

```bash
docker-compose exec web python run.py create-test-user
```

**Test Credentials**:
- Username: `testuser`
- Password: `password123`

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret...` | Yes |
| `FLASK_ENV` | Environment mode | `production` | Yes |
| `POSTGRES_DB` | Database name | `aceest_fitness` | Yes |
| `POSTGRES_USER` | Database username | `aceest_user` | Yes |
| `POSTGRES_PASSWORD` | Database password | `changeme123` | Yes |
| `WORKOUTS_PER_PAGE` | Pagination limit | `20` | No |
| `GUNICORN_WORKERS` | Number of workers | `4` | No |
| `GUNICORN_THREADS` | Threads per worker | `2` | No |

### Generate Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output to `SECRET_KEY` in your `.env` file.

---

## Services

### Web Service

**Container**: `aceest_web`  
**Image**: Custom Flask app  
**Port**: 5000  
**Health Check**: HTTP GET on `/`

**Features**:
- Multi-stage Docker build for optimization
- Non-root user for security
- Gunicorn production server
- Automatic database initialization
- Health checks every 30s

### Database Service

**Container**: `aceest_db`  
**Image**: `postgres:16-alpine`  
**Port**: 5432  
**Volume**: `aceest_postgres_data`

**Features**:
- Persistent data storage
- Automatic initialization
- Health checks via `pg_isready`
- Alpine Linux for minimal size

### Nginx Service

**Container**: `aceest_nginx`  
**Image**: `nginx:alpine`  
**Ports**: 80, 443  

**Features**:
- Reverse proxy to Flask app
- Gzip compression
- Security headers
- Static file caching
- SSL/TLS support (configure in nginx.conf)

---

## Commands

### Starting Services

```bash
# Start all services in background
docker-compose up -d

# Start with build
docker-compose up -d --build

# Start specific service
docker-compose up -d web

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v

# Stop specific service
docker-compose stop web
```

### Service Management

```bash
# Restart service
docker-compose restart web

# View running containers
docker-compose ps

# View resource usage
docker stats
```

### Database Operations

```bash
# Initialize database tables
docker-compose exec web python run.py init-db

# Create test user
docker-compose exec web python run.py create-test-user

# Access PostgreSQL shell
docker-compose exec db psql -U aceest_user -d aceest_fitness

# Backup database
docker-compose exec db pg_dump -U aceest_user aceest_fitness > backup.sql

# Restore database
docker-compose exec -T db psql -U aceest_user aceest_fitness < backup.sql
```

### Debugging

```bash
# Execute command in container
docker-compose exec web bash

# View container logs
docker-compose logs --tail=100 web

# Inspect container
docker inspect aceest_web

# View environment variables
docker-compose exec web env
```

### Building & Cleaning

```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Complete cleanup
docker system prune -a --volumes
```

---

## Troubleshooting

### Issue: Database Connection Failed

**Symptoms**: `Connection refused` or `could not connect to server`

**Solutions**:
1. Check database is running: `docker-compose ps`
2. Wait for health check: `docker-compose logs db`
3. Verify environment variables: `docker-compose config`
4. Restart services: `docker-compose restart`

### Issue: Port Already in Use

**Symptoms**: `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solutions**:
```bash
# Find process using port
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "5001:5000"  # Map to different host port
```

### Issue: Permission Denied

**Symptoms**: `Permission denied` when accessing volumes

**Solutions**:
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./logs ./instance

# Or run as root (not recommended)
docker-compose exec --user root web bash
```

### Issue: Image Build Fails

**Symptoms**: Build errors or package installation failures

**Solutions**:
```bash
# Clean build without cache
docker-compose build --no-cache

# Remove old images
docker image prune -a

# Check Dockerfile syntax
docker build -t test-build .
```

### Issue: Database Data Lost

**Symptoms**: Data disappears after restart

**Solutions**:
- Check volume exists: `docker volume ls`
- Don't use `docker-compose down -v` (removes volumes)
- Verify volume mount in docker-compose.yml

### View Health Status

```bash
# Check health of all containers
docker-compose ps

# Detailed health check
docker inspect aceest_web | grep -A 10 Health
```

---

## Production Deployment

### Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong `POSTGRES_PASSWORD`
- [ ] Enable HTTPS with SSL certificates
- [ ] Set `FLASK_ENV=production`
- [ ] Use environment variable secrets (not .env files)
- [ ] Enable firewall rules
- [ ] Regular backups configured
- [ ] Update Docker images regularly

### SSL/TLS Configuration

1. **Obtain SSL Certificate**:
   - Use Let's Encrypt: `certbot certonly --standalone -d your-domain.com`
   - Or use commercial certificate

2. **Update nginx.conf**:
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /etc/nginx/ssl/cert.pem;
       ssl_certificate_key /etc/nginx/ssl/key.pem;
       # ... rest of config
   }
   ```

3. **Mount certificates**:
   ```yaml
   volumes:
     - ./ssl:/etc/nginx/ssl:ro
   ```

### Performance Tuning

**Gunicorn Workers**:
```bash
# Formula: (2 × CPU_CORES) + 1
GUNICORN_WORKERS=9  # For 4 CPU cores
```

**Database Connection Pool**:
Edit `config.py`:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
}
```

### Monitoring

**Container Health**:
```bash
# Watch container status
watch docker-compose ps

# Monitor resource usage
docker stats
```

**Application Logs**:
```bash
# Follow logs
docker-compose logs -f --tail=100

# Export logs
docker-compose logs > app.log
```

### Backup Strategy

**Automated Backup Script**:
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U aceest_user aceest_fitness > "backup_${DATE}.sql"
```

**Schedule with Cron**:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Scaling

**Horizontal Scaling**:
```yaml
services:
  web:
    deploy:
      replicas: 3
```

**Load Balancing**:
Configure nginx upstream with multiple web instances.

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)

---

## Quick Reference

```bash
# Essential Commands
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View logs
docker-compose ps                 # List services
docker-compose restart web        # Restart service
docker-compose exec web bash      # Access container

# Database
docker-compose exec web python run.py init-db
docker-compose exec db psql -U aceest_user aceest_fitness

# Maintenance
docker-compose pull               # Update images
docker-compose build --no-cache   # Rebuild images
docker system prune -a            # Clean up
```

---

**Need Help?** Check the main [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md) for application-specific guidance.
