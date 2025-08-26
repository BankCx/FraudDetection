#!/usr/bin/env python3
"""
Simple test script for the Fraud Detection API
Usage: python test_api.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_predict():
    """Test the predict endpoint"""
    print("Testing /api/v1/predict...")
    
    # Test data
    transaction = {
        "amount": 150.50,
        "merchant_id": "amazon",
        "user_id": "user_1234",
        "ts": datetime.utcnow().isoformat() + "Z",
        "country": "US",
        "channel": "web"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/predict",
            json=transaction,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_metrics():
    """Test the metrics endpoint"""
    print("\nTesting /api/v1/metrics...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/metrics")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_dashboard():
    """Test the dashboard endpoint"""
    print("\nTesting / (dashboard)...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Response length: {len(response.text)} characters")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_sensitive_data():
    """Test the sensitive data endpoint"""
    print("\nTesting /api/v1/sensitive-data...")
    
    # Test without API key
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sensitive-data")
        print(f"Without API key - Status Code: {response.status_code}")
        
        # Test with API key
        response = requests.get(
            f"{BASE_URL}/api/v1/sensitive-data",
            headers={"X-API-Key": "test-api-key-123"}
        )
        print(f"With API key - Status Code: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_train_endpoint():
    """Test the train endpoint (legacy support)"""
    print("\nTesting /api/v1/train...")
    
    try:
        training_data = {
            "training_data": [
                {"amount": 100, "merchant_id": "test", "user_id": "user1", "ts": "2024-01-01T00:00:00Z", "country": "US", "channel": "web", "is_fraud": False}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/train",
            json=training_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Fraud Detection API Test Suite")
    print("=" * 40)
    
    tests = [
        ("Predict", test_predict),
        ("Metrics", test_metrics),
        ("Dashboard", test_dashboard),
        ("Sensitive Data", test_sensitive_data),
        ("Train", test_train_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:20} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

if __name__ == '__main__':
    main()
