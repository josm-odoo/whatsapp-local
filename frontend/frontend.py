from flask import request, jsonify, Flask, render_template,render_template_string
import logging
import random
import time
import hmac
import hashlib
import json
logger = logging.getLogger(__name__)
import sys
from pathlib import Path
from configs import config



def register_frontend_routes(app,traffic_log):
    """Register all frontend routes"""
    
    @app.route('/')
    def index():
        return render_template('index.html', page_title='Home',MOCK_PHONE_NUMBER_ID_1=config.MOCK_PHONE_NUMBER_ID_1,
            MOCK_APP_ID_1=config.MOCK_APP_ID_1,
            MOCK_APP_SECRET_1=config.MOCK_APP_SECRET_1,
            MOCK_WABA_ID_1=config.MOCK_WABA_ID_1,
            MOCK_ACCESS_TOKEN_1=config.MOCK_ACCESS_TOKEN_1,
            MOCK_WEBHOOK_TOKEN_1=config.MOCK_WEBHOOK_TOKEN_1,
            MOCK_PHONE_NUMBER_ID_2=config.MOCK_PHONE_NUMBER_ID_2,
            MOCK_APP_ID_2=config.MOCK_APP_ID_2,
            MOCK_APP_SECRET_2=config.MOCK_APP_SECRET_2,
            MOCK_WABA_ID_2=config.MOCK_WABA_ID_2,
            MOCK_ACCESS_TOKEN_2=config.MOCK_ACCESS_TOKEN_2,
            MOCK_WEBHOOK_TOKEN_2=config.MOCK_WEBHOOK_TOKEN_2)
    
    @app.route('/templates/<template_name>')
    def get_template(template_name):
        template_path = Path('templates') / template_name
        if template_path.exists() and template_path.is_file():
            with open(template_path, 'r') as file:
                return file.read()
        return "Template not found", 404
    
    @app.route('/message-templates')
    def get_whatsapp_template():
        template_path = Path('mock_data') / 'message_templates.json'
        if template_path.exists() and template_path.is_file():
            with open(template_path, 'r') as file:
                return file.read()
        return "Template not found", 404