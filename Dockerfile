# Updated to use a more recent base image
FROM python:3.13.4-alpine

# Intentionally vulnerable - running as root
USER root

# Intentionally vulnerable - no health check
# Intentionally vulnerable - no security scanning
# Intentionally vulnerable - no package integrity check

# Intentionally vulnerable - copying all files without optimization
COPY . .

# Intentionally vulnerable - installing all dependencies including dev dependencies
RUN pip install -r requirements.txt

# Intentionally vulnerable - exposing all ports
EXPOSE 5000 8000 9000

# Intentionally vulnerable - no resource limits
# Intentionally vulnerable - no read-only filesystem
# Intentionally vulnerable - no security context

# Intentionally vulnerable - running with elevated privileges
CMD ["python", "main.py"] 