# Bank of Checkmarx - Fraud Detection

A Python Flask-based fraud detection service for the Bank of Checkmarx demo application with intentionally vulnerable endpoints. This service handles transaction risk assessment, fraud scoring, and provides real-time fraud detection capabilities for the financial platform.

## Security Note

⚠️ **This is an intentionally vulnerable application for security testing purposes. Do not deploy in production or sensitive environments.**

## Overview

The Fraud Detection service is a Flask application that provides rule-based fraud detection capabilities including transaction risk assessment, fraud scoring, and suspicious activity monitoring. It provides comprehensive metrics and dashboard functionality.

## Key Features

- **Fraud Detection**: Rule-based transaction risk assessment and scoring
- **Transaction Analysis**: Real-time transaction monitoring and analysis
- **Risk Scoring**: Automated fraud risk calculation and labeling
- **Metrics Dashboard**: Live fraud metrics and statistics display
- **Request Tracking**: Unique request ID tracking for all operations
- **JWT Authentication**: Token-based API authentication
- **API Key Security**: API key authentication for sensitive endpoints
- **Health Monitoring**: Service health checks and dependency monitoring
- **Structured Logging**: Comprehensive error handling and logging
- **Template Rendering**: Jinja2 template engine for dashboard

## Technology Stack

- **Python 3.8+**: Programming language
- **Flask 1.1.4**: Web framework
- **Werkzeug 1.0.1**: WSGI utilities
- **Jinja2 2.11.3**: Template engine for dashboard
