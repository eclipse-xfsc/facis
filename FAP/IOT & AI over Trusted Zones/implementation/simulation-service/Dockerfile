# =============================================================================
# FACIS FAP IoT & AI — Simulation Service
# Multi-stage production Dockerfile
# =============================================================================
# Stage 1: builder  — compiles wheels from pyproject.toml
# Stage 2: runtime  — minimal image with only runtime dependencies
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build-time system deps for confluent-kafka (librdkafka)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only dependency metadata first (layer cache optimisation)
COPY pyproject.toml README.md ./

# Build wheels for all runtime dependencies
RUN pip install --no-cache-dir build && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# ---------------------------------------------------------------------------
# Stage 2 — Runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# OCI image labels (https://github.com/opencontainers/image-spec/blob/main/annotations.md)
LABEL org.opencontainers.image.title="facis-simulation-service" \
      org.opencontainers.image.description="Deterministic IoT simulation service for the FACIS FAP IoT & AI demonstrator" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="ATLAS IoT Lab GmbH" \
      org.opencontainers.image.source="https://github.com/siemens-2/facis" \
      org.opencontainers.image.authors="ATLAS IoT Lab GmbH"

WORKDIR /app

# Install only the runtime system library for confluent-kafka
RUN apt-get update && \
    apt-get install -y --no-install-recommends librdkafka1 curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages from pre-built wheels (no compiler needed)
COPY --from=builder /wheels /tmp/wheels
RUN pip install --no-cache-dir --no-deps /tmp/wheels/* && \
    rm -rf /tmp/wheels && \
    pip cache purge 2>/dev/null; true

# Copy application source
COPY src/ ./src/

# Copy runtime configuration
COPY config/ ./config/

# Copy API documentation (OpenAPI spec)
COPY docs/ ./docs/

# Copy license (required by Apache-2.0)
COPY LICENSE ./LICENSE

# Create non-root user (uid 1000)
RUN groupadd -g 1000 simulation && \
    useradd -u 1000 -g 1000 -m -s /bin/false simulation && \
    chown -R 1000:1000 /app

USER 1000

# Environment defaults (use SIMULATOR_ prefix per Pydantic Settings convention)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SIMULATOR_SIMULATION__SEED=12345 \
    SIMULATOR_SIMULATION__SPEED_FACTOR=1.0 \
    SIMULATOR_HTTP__HOST=0.0.0.0 \
    SIMULATOR_HTTP__PORT=8080 \
    SIMULATOR_MODBUS__PORT=502 \
    SIMULATOR_MQTT__HOST=localhost \
    SIMULATOR_MQTT__PORT=1883 \
    SIMULATOR_LOGGING__LEVEL=INFO

EXPOSE 8080 502

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/v1/health')"]

CMD ["python", "-m", "src.main"]
