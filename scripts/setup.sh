#!/bin/bash
# Setup script for Fraud Detection

echo "Setting up Fraud Detection..."

# Create required directories
mkdir -p logs
mkdir -p models

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Generate requirements.txt from requirements.in if pip-tools is available
if command -v pip-compile &> /dev/null; then
    echo "Compiling requirements..."
    pip-compile requirements.in
fi

echo "Setup complete! Run 'source venv/bin/activate' to activate the virtual environment."
