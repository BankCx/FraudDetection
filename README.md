# Bank of Checkmarx - Fraud Detection

This is the fraud detection application for the intentionally vulnerable Bank of Checkmarx demo application.

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

## Kafka Integration

### Start Consumer
```bash
python kafka_consumer.py
```

### Send Sample Transactions
```bash
# Send 10 transactions with 20% fraud ratio
python kafka_producer.py --count 10 --fraud-ratio 0.2

# Send 50 transactions with 30% fraud ratio, 2 second intervals
python kafka_producer.py --count 50 --fraud-ratio 0.3 --interval 2.0
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_BROKERS` | Kafka broker addresses | `localhost:9092` |
| `KAFKA_TOPIC_IN` | Input topic for transactions | `transactions` |
| `KAFKA_TOPIC_OUT` | Output topic for fraud alerts | `fraud-alerts` |
| `DATABASE_HOST` | PostgreSQL host | `localhost` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |
| `DATABASE_USERNAME` | Database username | `admin` |
| `DATABASE_PASSWORD` | Database password | `admin123` |
| `DATABASE_NAME` | Database name | `frauddetection` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password | `redis123` |
| `SECRET_KEY` | JWT secret key | `weak-secret-key-123` |
| `API_KEY` | API key for sensitive endpoints | `test-api-key-123` |

## Architecture

- **Main Application** (`fraud_detection.py`): Flask app with REST API endpoints
- **Service Layer** (`services/fraud_service.py`): Business logic and metrics tracking
- **Model Layer** (`models/fraud_model.py`): ML model wrapper with scikit-learn
- **Configuration** (`config/`): Database and security settings
- **Middleware** (`middleware/auth_middleware.py`): Authentication and logging
- **Infrastructure** (`kubernetes/`, `Dockerfile`): Deployment configuration

## Features

- Real-time fraud detection using machine learning
- REST API with request ID tracking
- HTML dashboard with live metrics
- Kafka integration for stream processing
- In-memory metrics and recent results tracking
- Jinja2 template filtering for risk highlighting
- Comprehensive error handling and logging

## Security Notes

⚠️ **This is an intentionally vulnerable demo application.** Do not use in production.

Known vulnerabilities include:
- SQL injection in database queries
- Command injection in training endpoint
- Unsafe pickle deserialization
- Weak cryptography (MD5, weak keys)
- Hardcoded credentials
- Insufficient input validation
