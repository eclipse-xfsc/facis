# Deployment Guide

## Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run locally
python -m src.main
```

## Docker

```bash
# Build image
docker build -t facis-simulation .

# Run container
docker run -p 8080:8080 -p 502:502 facis-simulation
```

## Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Production Deployment

1. Set environment variables for production
2. Use `docker-compose.yml` with production overrides
3. Configure external MQTT broker if needed
4. Set up monitoring and health checks
