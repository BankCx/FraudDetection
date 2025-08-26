#!/usr/bin/env python3
"""
Test script for external fraud scoring and notification services
"""

import requests
import json
import time

def test_enhanced_prediction():
    """Test the enhanced prediction API with external scoring"""
    print("🔍 Testing Enhanced Fraud Prediction with External Scoring...")
    
    # Test transaction data
    transaction_data = {
        "amount": 1500.75,
        "merchant_id": "suspicious_merchant_xyz",
        "user_id": "user_666",  # This user is blacklisted in our simulation
        "ts": "2024-01-15T14:30:00.000Z",
        "country": "NigeriA",  # Non-US country for higher risk
        "channel": "mobile",
        "ip_address": "192.168.1.100",
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/v1/predict',
            headers={'Content-Type': 'application/json'},
            json=transaction_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced Prediction Successful!")
            print(f"   Combined Risk Score: {result.get('risk_score', 0):.3f}")
            print(f"   Internal Score: {result.get('internal_score', 0):.3f}")
            print(f"   External Score: {result.get('external_score', 0):.3f}")
            print(f"   Final Label: {result.get('label', 'unknown')}")
            
            # Check if notifications were sent
            if 'notifications' in result:
                print(f"   🚨 Fraud Alert Notifications Sent:")
                notifications = result['notifications']
                for channel, results in notifications.get('channels', {}).items():
                    print(f"     - {channel.upper()}: {len(results)} alerts sent")
            
            # Show external assessment details
            external = result.get('external_assessment', {})
            if external:
                print(f"   External Providers Used: {len(external.get('providers_used', []))}")
                print(f"   Risk Factors: {', '.join(external.get('risk_factors', []))}")
            
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing prediction: {str(e)}")
        return False

def test_external_assessment():
    """Test the external assessment endpoint"""
    print("\n🔍 Testing External Assessment API...")
    
    transaction_data = {
        "amount": 750.00,
        "merchant_id": "amazon",
        "user_id": "user_1337",  # Another blacklisted user
        "country": "US",
        "channel": "web"
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/v1/external-assessment',
            headers={'Content-Type': 'application/json'},
            json=transaction_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ External Assessment Successful!")
            assessment = result.get('assessment', {})
            print(f"   Combined External Score: {assessment.get('combined_score', 0):.3f}")
            print(f"   Providers Used: {', '.join(assessment.get('providers_used', []))}")
            print(f"   Risk Factors: {', '.join(assessment.get('risk_factors', []))}")
            return True
        else:
            print(f"❌ External assessment failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing external assessment: {str(e)}")
        return False

def test_manual_alert():
    """Test the manual alert sending endpoint"""
    print("\n🔍 Testing Manual Alert Sending...")
    
    alert_data = {
        "transaction_data": {
            "id": "txn_manual_test_123",
            "amount": 999.99,
            "merchant_id": "suspicious_store",
            "user_id": "test_user_999",
            "country": "US",
            "channel": "mobile"
        },
        "risk_score": 0.85,
        "alert_config": {
            "sms_enabled": True,
            "phone_numbers": ["+1234567890"],
            "email_enabled": True,
            "email_addresses": ["test@example.com"],
            "slack_enabled": True,
            "slack_channels": ["#test-alerts"]
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/v1/send-alert',
            headers={'Content-Type': 'application/json'},
            json=alert_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manual Alert Successful!")
            notification_result = result.get('notification_result', {})
            channels = notification_result.get('channels', {})
            
            for channel_type, channel_results in channels.items():
                print(f"   {channel_type.upper()}: {len(channel_results)} notifications sent")
                for notification in channel_results:
                    status = notification.get('status', 'unknown')
                    provider = notification.get('provider', 'unknown')
                    print(f"     - {provider}: {status}")
            
            return True
        else:
            print(f"❌ Manual alert failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual alert: {str(e)}")
        return False

def test_fraud_providers():
    """Test the fraud providers status endpoint"""
    print("\n🔍 Testing Fraud Providers Status...")
    
    try:
        response = requests.get('http://localhost:5000/api/v1/fraud-providers')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fraud Providers Status Retrieved!")
            print(f"   Total Providers: {result.get('total_providers', 0)}")
            print(f"   Active Providers: {result.get('active_providers', 0)}")
            
            providers = result.get('providers', {})
            for provider_id, provider_info in providers.items():
                name = provider_info.get('name', provider_id)
                status = provider_info.get('status', 'unknown')
                configured = provider_info.get('api_key_configured', False) or provider_info.get('secret_configured', False)
                print(f"   - {name}: {status} (configured: {configured})")
            
            return True
        else:
            print(f"❌ Providers status failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing providers status: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting External Services Test Suite for Bank of Checkmarx Fraud Detection")
    print("=" * 70)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    test_results = []
    
    # Run tests
    test_results.append(test_enhanced_prediction())
    test_results.append(test_external_assessment())
    test_results.append(test_manual_alert())
    test_results.append(test_fraud_providers())
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(test_results)
    total = len(test_results)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! External fraud scoring and notifications are working.")
    else:
        print("❌ Some tests failed. Check the server logs for details.")
    
    print("\n🔧 New Features Added:")
    print("   1. External Fraud Scoring APIs (FraudScore, Sift Science, Risk Intelligence)")
    print("   2. Multi-channel Notification System (SMS, Email, Slack)")
    print("   3. Enhanced Prediction API with combined scoring")
    print("   4. Manual alert triggering")
    print("   5. Provider status monitoring")
    print("\n🔑 Hardcoded Secrets Added:")
    print("   - FRAUD_SCORE_API_KEY")
    print("   - RISK_INTEL_SECRET") 
    print("   - SIFT_SCIENCE_API_KEY")
    print("   - TWILIO_AUTH_TOKEN & TWILIO_ACCOUNT_SID")
    print("   - SENDGRID_API_KEY")
    print("   - SLACK_WEBHOOK_SECRET")

if __name__ == "__main__":
    main()
