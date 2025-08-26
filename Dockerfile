FROM python:3.13.4-alpine

USER root

# Install build dependencies for psycopg and other packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev

WORKDIR /app

COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies to reduce image size
RUN apk del gcc musl-dev linux-headers

COPY . .

EXPOSE 5000

CMD ["python", "fraud_detection.py"] 