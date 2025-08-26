# Multi-stage build for optimized testing and production
FROM python:3.13.4-alpine AS base

# Install system dependencies and create non-root user in one layer
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    && adduser -D -s /bin/sh appuser \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy requirements and install Python dependencies in one layer
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Development/Testing stage
FROM base AS development
RUN pip install --no-cache-dir pytest flask-testing
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
CMD ["python", "fraud_detection.py"]

# Production stage
FROM base AS production
COPY . .
RUN chown -R appuser:appuser /app \
    && python -m py_compile fraud_detection.py
USER appuser
EXPOSE 5000
CMD ["python", "fraud_detection.py"] 