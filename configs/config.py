"""
Global configuration for mock WhatsApp API
All credentials are hard-coded for testing purposes
"""

# Mock credentials - change these if needed
import os


MOCK_PHONE_NUMBER_ID_1 = "11111111"
MOCK_APP_ID_1 = "11111111"
MOCK_APP_SECRET_1 = "11111111"
MOCK_WABA_ID_1 = "11111111"
MOCK_ACCESS_TOKEN_1 = "11111111"
MOCK_WEBHOOK_TOKEN_1 = "Mock 1 webhook token"

MOCK_PHONE_NUMBER_ID_2 = "22222222"
MOCK_APP_ID_2 = "22222222"
MOCK_APP_SECRET_2 = "22222222"
MOCK_WABA_ID_2 = "22222222"
MOCK_ACCESS_TOKEN_2 = "22222222"
MOCK_WEBHOOK_TOKEN_2 = "Mock 2 webhook token"


MOCK_WEBHOOK_URL = "http://localhost:8569/whatsapp/webhook"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))