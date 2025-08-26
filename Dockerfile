FROM python:3.13.4-alpine

USER root

# Install build dependencies for psycopg and other packages
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev \
    curl

WORKDIR /app

COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies to reduce image size
RUN apk del gcc g++ musl-dev linux-headers

COPY . .

EXPOSE 5000

# Add healthcheck to monitor container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "fraud_detection.py"] 