"""
Global configuration for mock WhatsApp API
All credentials are hard-coded for testing purposes
"""

# Mock credentials - change these if needed
import os


MOCK_PHONE_NUMBER_ID = "11111111"
MOCK_APP_ID = "11111111"
MOCK_APP_SECRET = "11111111"
MOCK_WABA_ID = "11111111"
MOCK_ACCESS_TOKEN = "11111111"
MOCK_WEBHOOK_TOKEN = "webhook token"
MOCK_WEBHOOK_URL = "http://localhost:8569/whatsapp/webhook"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))