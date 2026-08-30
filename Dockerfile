# Multi-stage production Dockerfile for LogPilot AI
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies needed for C++ builds and FAISS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final runtime image
FROM python:3.11-slim as runner

WORKDIR /app

# Copy installed python dependencies
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Set Environment Variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "production_rag.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
