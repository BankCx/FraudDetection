import requests
import json
import base64
import hashlib
from datetime import datetime
from config.security import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, SENDGRID_API_KEY, SLACK_WEBHOOK_SECRET

class NotificationService:
    """Notification service for fraud alerts via multiple channels"""
    
    def __init__(self):
        self.twilio_sid = TWILIO_ACCOUNT_SID
        self.twilio_token = TWILIO_AUTH_TOKEN
        self.sendgrid_key = SENDGRID_API_KEY
        self.slack_webhook = SLACK_WEBHOOK_SECRET
        
        # Service endpoints
        self.twilio_base_url = "https://api.twilio.com/2010-04-01"
        self.sendgrid_base_url = "https://api.sendgrid.com/v3"
        self.slack_webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    
    def send_fraud_alert_sms(self, phone_number, transaction_data, risk_score):
        """Send SMS fraud alert via Twilio"""
        try:
            # Prepare Twilio authentication
            auth_string = f"{self.twilio_sid}:{self.twilio_token}"
            auth_header = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Create alert message
            alert_message = self._create_sms_alert_message(transaction_data, risk_score)
            
            payload = {
                'To': phone_number,
                'From': '+15551234567',  # Twilio phone number
                'Body': alert_message
            }
            
            # Simulate Twilio SMS API call
            response = self._simulate_twilio_response(payload)
            
            return {
                'status': 'sent',
                'provider': 'Twilio',
                'message_sid': response.get('sid'),
                'to': phone_number,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"SMS notification error: {str(e)}")
            return {
                'status': 'failed',
                'provider': 'Twilio',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_fraud_alert_email(self, email_address, transaction_data, risk_score, external_scores=None):
        """Send email fraud alert via SendGrid"""
        try:
            headers = {
                'Authorization': f'Bearer {self.sendgrid_key}',
                'Content-Type': 'application/json'
            }
            
            # Create detailed email content
            email_content = self._create_email_alert_content(transaction_data, risk_score, external_scores)
            
            payload = {
                'personalizations': [{
                    'to': [{'email': email_address}],
                    'subject': f'🚨 Fraud Alert - High Risk Transaction Detected'
                }],
                'from': {
                    'email': 'security@bankofcheckmarx.com',
                    'name': 'Bank of Checkmarx Security'
                },
                'content': [{
                    'type': 'text/html',
                    'value': email_content
                }],
                'categories': ['fraud-alert', 'security'],
                'custom_args': {
                    'transaction_id': transaction_data.get('id', 'unknown'),
                    'risk_score': str(risk_score),
                    'alert_type': 'fraud_detection'
                }
            }
            
            # Simulate SendGrid API call
            response = self._simulate_sendgrid_response(payload)
            
            return {
                'status': 'sent',
                'provider': 'SendGrid',
                'message_id': response.get('message_id'),
                'to': email_address,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Email notification error: {str(e)}")
            return {
                'status': 'failed',
                'provider': 'SendGrid',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_slack_alert(self, channel, transaction_data, risk_score, external_scores=None):
        """Send Slack notification for fraud alert"""
        try:
            headers = {
                'Authorization': f'Bearer {self.slack_webhook}',
                'Content-Type': 'application/json'
            }
            
            # Create Slack message with rich formatting
            slack_payload = self._create_slack_alert_payload(channel, transaction_data, risk_score, external_scores)
            
            # Simulate Slack webhook call
            response = self._simulate_slack_response(slack_payload)
            
            return {
                'status': 'sent',
                'provider': 'Slack',
                'channel': channel,
                'timestamp': datetime.now().isoformat(),
                'message_ts': response.get('ts')
            }
            
        except Exception as e:
            print(f"Slack notification error: {str(e)}")
            return {
                'status': 'failed',
                'provider': 'Slack',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_comprehensive_alert(self, alert_config, transaction_data, risk_score, external_scores=None):
        """Send fraud alert via multiple channels based on configuration"""
        try:
            results = {
                'alert_id': f"alert_{int(datetime.now().timestamp())}",
                'transaction_id': transaction_data.get('id', 'unknown'),
                'risk_score': risk_score,
                'channels': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # SMS notifications
            if alert_config.get('sms_enabled') and alert_config.get('phone_numbers'):
                sms_results = []
                for phone in alert_config['phone_numbers']:
                    sms_result = self.send_fraud_alert_sms(phone, transaction_data, risk_score)
                    sms_results.append(sms_result)
                results['channels']['sms'] = sms_results
            
            # Email notifications
            if alert_config.get('email_enabled') and alert_config.get('email_addresses'):
                email_results = []
                for email in alert_config['email_addresses']:
                    email_result = self.send_fraud_alert_email(email, transaction_data, risk_score, external_scores)
                    email_results.append(email_result)
                results['channels']['email'] = email_results
            
            # Slack notifications
            if alert_config.get('slack_enabled') and alert_config.get('slack_channels'):
                slack_results = []
                for channel in alert_config['slack_channels']:
                    slack_result = self.send_slack_alert(channel, transaction_data, risk_score, external_scores)
                    slack_results.append(slack_result)
                results['channels']['slack'] = slack_results
            
            return results
            
        except Exception as e:
            print(f"Comprehensive alert error: {str(e)}")
            return {
                'alert_id': f"alert_error_{int(datetime.now().timestamp())}",
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_sms_alert_message(self, transaction_data, risk_score):
        """Create SMS alert message"""
        amount = transaction_data.get('amount', 0)
        merchant = transaction_data.get('merchant_id', 'Unknown')
        user_id = transaction_data.get('user_id', 'Unknown')
        
        return (f"🚨 FRAUD ALERT: High-risk transaction detected!\n"
                f"Amount: ${amount:.2f}\n"
                f"Merchant: {merchant}\n"
                f"Risk Score: {risk_score:.2f}\n"
                f"User: {user_id}\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
                f"Call security immediately if unauthorized.")
    
    def _create_email_alert_content(self, transaction_data, risk_score, external_scores=None):
        """Create detailed HTML email content"""
        amount = transaction_data.get('amount', 0)
        merchant = transaction_data.get('merchant_id', 'Unknown')
        user_id = transaction_data.get('user_id', 'Unknown')
        country = transaction_data.get('country', 'Unknown')
        channel = transaction_data.get('channel', 'Unknown')
        
        external_info = ""
        if external_scores:
            external_info = f"""
            <h3>External Risk Assessment</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td><strong>Combined Score:</strong></td>
                    <td>{external_scores.get('combined_score', 0):.3f}</td>
                </tr>
                <tr>
                    <td><strong>Risk Factors:</strong></td>
                    <td>{', '.join(external_scores.get('risk_factors', []))}</td>
                </tr>
                <tr>
                    <td><strong>Providers:</strong></td>
                    <td>{', '.join(external_scores.get('providers_used', []))}</td>
                </tr>
            </table>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert-header {{ background-color: #ff4444; color: white; padding: 15px; text-align: center; }}
                .transaction-details {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; }}
                .risk-score {{ font-size: 24px; font-weight: bold; color: #ff4444; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                td {{ padding: 8px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="alert-header">
                <h1>🚨 FRAUD ALERT - IMMEDIATE ACTION REQUIRED</h1>
            </div>
            
            <div class="transaction-details">
                <h2>High-Risk Transaction Detected</h2>
                <p>A transaction with a high fraud risk score has been detected and requires immediate review.</p>
                
                <h3>Transaction Details</h3>
                <table>
                    <tr><td><strong>Amount:</strong></td><td>${amount:.2f}</td></tr>
                    <tr><td><strong>Merchant:</strong></td><td>{merchant}</td></tr>
                    <tr><td><strong>User ID:</strong></td><td>{user_id}</td></tr>
                    <tr><td><strong>Country:</strong></td><td>{country}</td></tr>
                    <tr><td><strong>Channel:</strong></td><td>{channel}</td></tr>
                    <tr><td><strong>Timestamp:</strong></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</td></tr>
                </table>
                
                <h3>Risk Assessment</h3>
                <p class="risk-score">Risk Score: {risk_score:.3f} / 1.000</p>
                
                {external_info}
                
                <h3>Recommended Actions</h3>
                <ul>
                    <li>Review transaction details immediately</li>
                    <li>Contact customer to verify transaction legitimacy</li>
                    <li>Consider temporary account restrictions if necessary</li>
                    <li>Document all findings in the fraud case management system</li>
                </ul>
            </div>
            
            <p><strong>This is an automated security alert from Bank of Checkmarx Fraud Detection System.</strong></p>
        </body>
        </html>
        """
    
    def _create_slack_alert_payload(self, channel, transaction_data, risk_score, external_scores=None):
        """Create Slack alert payload with rich formatting"""
        amount = transaction_data.get('amount', 0)
        merchant = transaction_data.get('merchant_id', 'Unknown')
        user_id = transaction_data.get('user_id', 'Unknown')
        
        # Risk level emoji
        risk_emoji = "🔴" if risk_score > 0.7 else "🟡" if risk_score > 0.4 else "🟢"
        
        # External scores summary
        external_text = ""
        if external_scores:
            external_text = f"\n*External Assessment:* {external_scores.get('combined_score', 0):.3f}"
            if external_scores.get('risk_factors'):
                external_text += f"\n*Risk Factors:* {', '.join(external_scores.get('risk_factors', [])[:3])}"
        
        return {
            'channel': channel,
            'username': 'Fraud Detection Bot',
            'icon_emoji': ':warning:',
            'attachments': [
                {
                    'color': 'danger' if risk_score > 0.7 else 'warning',
                    'title': f'{risk_emoji} High-Risk Transaction Alert',
                    'title_link': 'https://frauddetection.bankofcheckmarx.com/dashboard',
                    'fields': [
                        {
                            'title': 'Amount',
                            'value': f'${amount:.2f}',
                            'short': True
                        },
                        {
                            'title': 'Risk Score',
                            'value': f'{risk_score:.3f}',
                            'short': True
                        },
                        {
                            'title': 'Merchant',
                            'value': merchant,
                            'short': True
                        },
                        {
                            'title': 'User ID',
                            'value': user_id,
                            'short': True
                        }
                    ],
                    'footer': f'Bank of Checkmarx Fraud Detection{external_text}',
                    'ts': int(datetime.now().timestamp()),
                    'actions': [
                        {
                            'type': 'button',
                            'text': 'Review Transaction',
                            'url': f'https://frauddetection.bankofcheckmarx.com/transaction/{transaction_data.get("id", "unknown")}'
                        },
                        {
                            'type': 'button',
                            'text': 'Block User',
                            'style': 'danger',
                            'confirm': {
                                'title': 'Block User Account?',
                                'text': f'Are you sure you want to block user {user_id}?',
                                'ok_text': 'Block',
                                'dismiss_text': 'Cancel'
                            }
                        }
                    ]
                }
            ]
        }
    
    def _simulate_twilio_response(self, payload):
        """Simulate Twilio API response"""
        return {
            'sid': f'SM{hashlib.md5(payload["To"].encode()).hexdigest()[:32]}',
            'status': 'queued',
            'to': payload['To'],
            'from': payload['From'],
            'body': payload['Body'][:50] + '...',
            'price': '-0.0075',
            'price_unit': 'USD'
        }
    
    def _simulate_sendgrid_response(self, payload):
        """Simulate SendGrid API response"""
        email_hash = hashlib.md5(payload['personalizations'][0]['to'][0]['email'].encode()).hexdigest()
        return {
            'message_id': f'sendgrid_{email_hash[:16]}',
            'status': 'queued',
            'to': payload['personalizations'][0]['to'][0]['email']
        }
    
    def _simulate_slack_response(self, payload):
        """Simulate Slack webhook response"""
        return {
            'ok': True,
            'channel': payload['channel'],
            'ts': str(int(datetime.now().timestamp())) + '.000000',
            'message': {
                'text': payload.get('text', ''),
                'username': payload.get('username', 'bot')
            }
        }
