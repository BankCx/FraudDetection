# Bank of Checkmarx - Fraud Detection (Simplified)

This is the simplified fraud detection application for the intentionally vulnerable Bank of Checkmarx demo application.

## Recommended Checkmarx One Configuration
- Criticality: 3
- Cloud Insights: Yes
- Internet-facing: No

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run the Application
```bash
python fraud_detection.py
```

The application will be available at:
- Dashboard: http://localhost:5000/
- API: http://localhost:5000/api/v1/

## API Usage

### Predict Fraud
```bash
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.50,
    "merchant_id": "amazon",
    "user_id": "user_1234",
    "ts": "2024-01-15T10:30:00.000Z",
    "country": "US",
    "channel": "web"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_score": 0.234,
  "label": "legit",
  "echo": {
    "amount": 150.50,
    "merchant_id": "amazon",
    "user_id": "user_1234",
    "ts": "2024-01-15T10:30:00.000Z",
    "country": "US",
    "channel": "web"
  }
}
```

### Get Metrics
```bash
curl http://localhost:5000/api/v1/metrics
```

Response:
```json
{
  "total": 150,
  "fraud_rate": 0.12,
  "last_hour_avg": 2.5,
  "last_hour_fraud_rate": 0.08,
  "last_update": "2024-01-15T10:30:00.000000"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | PostgreSQL host | `localhost` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |
| `DATABASE_USERNAME` | Database username | `admin` |
| `DATABASE_PASSWORD` | Database password | `admin123` |
| `DATABASE_NAME` | Database name | `frauddetection` |
| `SECRET_KEY` | JWT secret key | `weak-secret-key-123` |
| `API_KEY` | API key for sensitive endpoints | `test-api-key-123` |

## Architecture

- **Main Application** (`fraud_detection.py`): Flask app with REST API endpoints
- **Service Layer** (`services/fraud_service.py`): Business logic and metrics tracking
- **Model Layer** (`models/fraud_model.py`): Rule-based fraud detection
- **Configuration** (`config/`): Database and security settings
- **Middleware** (`middleware/auth_middleware.py`): Authentication and logging
- **Infrastructure** (`Dockerfile`): Simple container deployment

## Features

- Rule-based fraud detection (simplified from ML)
- REST API with request ID tracking
- HTML dashboard with live metrics
- In-memory metrics and recent results tracking
- Jinja2 template filtering for risk highlighting
- Comprehensive error handling and logging
- JWT token validation
- API key authentication
- PostgreSQL database integration (for SQL injection demo)

## Security Notes

⚠️ **This is an intentionally vulnerable demo application.** Do not use in production.

Known vulnerabilities include:
- SQL injection in database queries
- Unsafe pickle deserialization
- Weak cryptography (MD5, weak keys)
- Hardcoded credentials
- Insufficient input validation

## Simplification Changes

This application has been simplified from the original version:

### Removed Components:
- Kafka messaging system
- Machine learning libraries (scikit-learn, TensorFlow, pandas, numpy)
- Redis caching
- Complex model training/retraining
- Kubernetes orchestration
- Multiple database systems

### Retained Components:
- Core Flask web application
- Rule-based fraud detection
- JWT authentication
- PostgreSQL database (for vulnerability demo)
- Docker containerization
- Basic security features

### Dependencies Reduced:
- From 13 packages to 6 packages
- 54% reduction in external dependencies
- Simplified deployment and maintenance
