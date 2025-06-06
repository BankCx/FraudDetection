# Intentionally vulnerable - using outdated base image
FROM python:3.8-slim

# Intentionally vulnerable - running as root
USER root

# Intentionally vulnerable - no healthcheck
# Intentionally vulnerable - no non-root user
# Intentionally vulnerable - no security scanning

WORKDIR /app

# Intentionally vulnerable - copying requirements first (bad layer caching)
COPY requirements.txt .

# Intentionally vulnerable - no package integrity check
RUN pip install --no-cache-dir -r requirements.txt

# Intentionally vulnerable - copying all files
COPY . .

# Intentionally vulnerable - no build optimization
# Intentionally vulnerable - no security scanning
# Intentionally vulnerable - no resource limits

# Intentionally vulnerable - exposing all ports
EXPOSE 5000

# Intentionally vulnerable - running as root
CMD ["python", "fraud_detection.py"]

# Intentionally vulnerable - no healthcheck
# Intentionally vulnerable - no security context
# Intentionally vulnerable - no read-only filesystem 