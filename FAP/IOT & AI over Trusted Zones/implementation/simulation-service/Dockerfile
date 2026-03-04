# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir build && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install dependencies from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code and OpenAPI spec (used by /docs and /redoc)
COPY src/ ./src/
COPY config/ ./config/
COPY docs/ ./docs/

# Create non-root user
RUN useradd -m -u 1000 simulation && \
    chown -R simulation:simulation /app
USER simulation

# Environment defaults
ENV SIMULATION_SEED=12345 \
    TIME_ACCELERATION=1 \
    HTTP_PORT=8080 \
    MODBUS_PORT=502 \
    MQTT_BROKER=localhost \
    MQTT_PORT=1883

EXPOSE 8080 502

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

CMD ["python", "-m", "src.main"]
