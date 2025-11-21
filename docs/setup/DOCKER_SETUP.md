# Docker Setup Guide

This guide explains how to run PostgreSQL using Docker Compose for the standmate-be project.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

1. **Create your `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Start PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

3. **Verify the database is running**:
   ```bash
   docker-compose ps
   ```

4. **Run your FastAPI application**:
   ```bash
   cd app
   uvicorn main:app --reload
   ```

## Common Commands

### Start the database
```bash
docker-compose up -d
```

### Stop the database
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes all data)
```bash
docker-compose down -v
```

### View logs
```bash
docker-compose logs -f postgres
```

### Connect to PostgreSQL CLI
```bash
docker-compose exec postgres psql -U user -d mydb
```

## Optional: Enable pgAdmin

To use pgAdmin (web-based database management tool):

1. Uncomment the `pgadmin` section in `docker-compose.yml`
2. Restart Docker Compose:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
3. Access pgAdmin at http://localhost:5050
4. Login with credentials from `.env` file (default: admin@admin.com / admin)

## Configuration

All database configuration is managed through the `.env` file:

- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `POSTGRES_PORT`: Port to expose PostgreSQL (default: 5432)
- `DATABASE_URL`: Connection string for FastAPI application

## Troubleshooting

### Port already in use
If port 5432 is already in use, change `POSTGRES_PORT` in your `.env` file:
```
POSTGRES_PORT=5433
```

Then update `DATABASE_URL` accordingly:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/mydb
```

### Database connection refused
Make sure the database is healthy:
```bash
docker-compose ps
```

The status should show "healthy". If not, check logs:
```bash
docker-compose logs postgres
```

### Reset database
To start fresh with a clean database:
```bash
docker-compose down -v
docker-compose up -d
```
