# ==============================================================================
# AURA-Code Intelligence Platform - Production Dockerfile
# Samsung PRISM GenAI Hackathon 3.0 (Theme 01: Agentic Code Intelligence)
# 100% CPU Optimized - Zero GPU Dependency - Pure Local Inference
# ==============================================================================

FROM python:3.13-slim

WORKDIR /app

# Install system utilities and Node.js for sample voice assistant runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy full application source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Pre-run test suite during build to guarantee artifact integrity
RUN python -m pytest tests/ -v

# Expose API and UI port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch FastAPI ASGI server
CMD ["uvicorn", "engine.server:app", "--host", "0.0.0.0", "--port", "8000"]
