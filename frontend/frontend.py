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
        return render_template('index.html', page_title='Home',mock_phone_number_id=config.MOCK_PHONE_NUMBER_ID,
            mock_app_id=config.MOCK_APP_ID,
            mock_app_secret=config.MOCK_APP_SECRET,
            mock_waba_id=config.MOCK_WABA_ID,
            mock_access_token=config.MOCK_ACCESS_TOKEN,
            mock_webhook_token=config.MOCK_WEBHOOK_TOKEN)

    @app.route('/traffic-logs', methods=['GET'])
    def traffic_logs():
        return jsonify(list(reversed(traffic_log)))
    
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