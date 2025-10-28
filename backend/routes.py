from flask import request, jsonify
import logging
import random
import time
import hmac
import hashlib
import json
import os
from datetime import datetime
from configs import config


logger = logging.getLogger(__name__)


def register_backend_routes(app):
    """Register all webhook/API routes"""

   
    @app.route('/v<version>/<phone_number_id>/phone_numbers', methods=['GET'])
    def test_connection(version, phone_number_id):

        logger.info(f"Get Phone Numbers - Version: {version}, Phone ID: {phone_number_id}")

        return jsonify({
            'data': [{
                'verified_name': 'Whats App Mock Business',
                'display_phone_number': f"{phone_number_id}",
                'id': f"{phone_number_id}",
                'quality_rating': 'GREEN'
            }]
        }), 200
    
    @app.route('/v<version>/<phone_number_id>/uploads', methods=['POST'])
    def post_uploads(version, phone_number_id):
        '''Mock endpoint for creating upload sessions  '''
        access_token = request.args.get('access_token')
        if not access_token or access_token != config.MOCK_ACCESS_TOKEN:
            logger.error(f"Invalid or missing access token for phone ID: {phone_number_id}")
            return jsonify({
                'error': {
                    'message': 'Invalid OAuth access token.',
                    'type': 'OAuthException',
                    'code': 190,
                    'fbtrace_id': 'mock_trace_id'
                }
            }), 401
        if phone_number_id != config.MOCK_PHONE_NUMBER_ID:
            logger.error(f"Phone number ID {phone_number_id} not found.")
            return jsonify({
                'error': {
                    'message': 'Phone number ID not found.',
                    'type': 'OAuthException',
                    'code': 100,
                    'fbtrace_id': 'mock_trace_id'
                }
            }), 404
        logger.info(f"Create Upload Session - Version: {version}, Phone ID: {phone_number_id}")
        return jsonify({
            'id': f'upload_session_{random.randint(1000000000, 9999999999)}',
        }), 200
    
    @app.route('/v<version>/<phone_number_id>/message_templates', methods=['POST', 'GET'])
    def message_templates(version, phone_number_id):
        # Extract Bearer token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '', 1)

        if token != config.MOCK_ACCESS_TOKEN:
            return jsonify({
                'error': {
                    'message': 'Invalid OAuth access token.',
                    'type': 'OAuthException',
                    'code': 190,
                    'fbtrace_id': 'mock_trace_id'
                }
            }), 401
        if request.method == 'POST':
            # Create new template
            data = request.get_json()

            template_name = data.get('name', 'unnamed_template')
            language = data.get('language', 'en')
            category = data.get('category', 'MARKETING')
            components = data.get('components', [])
            template_id = str(random.randint(1000000000000000, 9999999999999999))
            template_response = {
                'name': template_name,
                'components': components,
                'language': language if '_' in language else f"{language}_US",
                'status': 'APPROVED',
                'category': category,
                'id': template_id,
                'quality_score': {
                    'score': 'unknown'
                }
            }
            try:
                with open(os.path.join(config.ROOT_DIR,"mock_data/message_templates.json"),"r+") as f:
                    json_data = f.read()
                    templates = json.loads(json_data) if json_data else []
                    templates.append(template_response)
                    f.seek(0)
                    json.dump(templates, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving message template: {e}")
            logger.info(f"Create Message Template - Version: {version}, Phone ID: {phone_number_id}")
            return jsonify({
                'id': template_id,
                'status': 'APPROVED', # Automatically approve it for now
                'data': [template_response],
                'paging': {
                    'cursors': {
                        'before': 'MAZDZD',
                        'after': 'MjQZD'
                    }
                }
            }), 200
        if request.method == 'GET':
            logger.info(f"Get Message - Templates - Version: {version}, Phone ID: {phone_number_id}")
            try:
                with open(os.path.join(config.ROOT_DIR, "mock_data/message_templates.json")) as f:
                    json_data = f.read()
                    templates = json.loads(json_data)

            except Exception as e:
                logger.error(f"Error loading message templates: {e}")
            return jsonify({
                'data': templates,
                'paging': {
                    'cursors': {
                        'before': 'MAZDZD',
                        'after': 'MjQZD'
                    }
                }
            }), 200

    @app.route('/set-odoo-whatsapp-webhook', methods=['POST'])
    def set_odoo_whatsapp_webhook():
        data = request.json
        config.MOCK_WEBHOOK_TOKEN = data.get('webhook_token')
        logger.info(f"Updated webhook token to: {config.MOCK_WEBHOOK_TOKEN}")
        return jsonify(data)
    
    @app.route('/send-manual-webhook-message', methods=['POST'])
    def send_manual_webhook():

        data = request.json

        webhook_url = config.MOCK_WEBHOOK_URL
        phone_number_id = config.MOCK_PHONE_NUMBER_ID
        access_token = config.MOCK_ACCESS_TOKEN
        webhook_token = config.MOCK_WEBHOOK_TOKEN
        from_number = data.get('from_phone_number')
        message_text = data.get('message')
        app_secret = config.MOCK_APP_SECRET
        app_id = config.MOCK_APP_ID
        waba_id = config.MOCK_WABA_ID
        access_token = config.MOCK_ACCESS_TOKEN
        webhook_token = config.MOCK_WEBHOOK_TOKEN

        logger.info(f"Manual message request - From: {from_number}, To webhook: {webhook_url}")
                # Validate inputs
        if not all([webhook_url, phone_number_id, from_number, message_text]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": waba_id if waba_id else phone_number_id,
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": phone_number_id,
                            "phone_number_id": phone_number_id
                        },
                        "contacts": [{
                            "profile": {"name": "Dashboard User"},
                            "wa_id": from_number
                        }],
                        "messages": [{
                            "from": from_number,
                            "id": f"wamid.manual_{random.randint(1000000, 9999999)}",
                            "timestamp": str(int(time.time())),
                            "text": {"body": message_text},
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        # Generate X-Hub-Signature-256 header if app_secret is provided
        headers = {'Content-Type': 'application/json'}

        # Convert payload to JSON bytes (this MUST be the exact bytes sent)
        payload_bytes = json.dumps(webhook_payload, separators=(',', ':')).encode('utf-8')

        if app_secret:
            # Generate HMAC SHA256 signature from the exact payload bytes
            signature = hmac.new(
                app_secret.encode('utf-8'),
                msg=payload_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()

            # Add signature header in the format: sha256=<hex_signature>
            headers['X-Hub-Signature-256'] = f'sha256={signature}'
            logger.info(f"Generated X-Hub-Signature-256: sha256={signature}")
            logger.info(f"Payload bytes length: {len(payload_bytes)}")
        else:
            logger.warning("No app_secret provided, skipping signature generation")
        
        # Send to webhook with custom headers
        # IMPORTANT: Use 'data' not 'json' to send the exact bytes we signed
        try:
            import requests
            response = requests.post(
                webhook_url,
                data=payload_bytes,  # Send exact bytes, not json parameter
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            logger.info(f"Manual message sent successfully to {webhook_url}")
            return jsonify({
                'success': True,
                'message': 'Message sent successfully',
                'signature_included': bool(app_secret)
            }), 200

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send manual message: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    

    @app.route('/v<version>/<phone_number_id>/messages', methods=['POST'])
    def send_message(version, phone_number_id):
        """Mock endpoint for sending WhatsApp messages via Graph API"""
        data = request.get_json()
        logger.info(f"Send Message Request - Version: {version}, Phone ID: {phone_number_id}")
        logger.info(f"Message Data: {data}")

        # Extract recipient and message details
        to_number = data.get('to', '')

        # Return success response
        return jsonify({
            'messaging_product': 'whatsapp',
            'contacts': [{'input': to_number, 'wa_id': to_number}],
            'messages': [{'id': f'mock_message_id_{random.randint(10000, 99999)}'}]
        }), 200