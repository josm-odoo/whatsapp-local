from flask import request, jsonify
import logging
import random
import time
import hmac
import hashlib
import json
from configs import config
from backend.mock_whatsapp import MockWhatsApp

logger = logging.getLogger(__name__)
mock = MockWhatsApp


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
        '''Mock endpoint for creating upload sessions'''
        if not mock.validate_access_token_param(request):
            return jsonify(*mock.oauth_error(
                'Invalid OAuth access token. Failed at endpoint "/v<version>/<phone_number_id>/uploads"'
            ))
        if not mock.is_valid_phone_id(phone_number_id):
            logger.error(f"Phone number ID {phone_number_id} not found.")
            return jsonify(*mock.not_found_error('Phone number ID not found.'))
        logger.info(f"Create Upload Session - Version: {version}, Phone ID: {phone_number_id}")
        return jsonify({'id': mock.generate_upload_session_id()}), 200

    @app.route('/v<version>/upload_session_<session_id>', methods=['POST'])
    def resumable_upload(version, session_id):
        if not mock.validate_access_token_param(request):
            return jsonify(*mock.oauth_error())
        file_length = request.args.get('file_length', '0')
        file_type = request.args.get('file_type', 'application/octet-stream')
        logger.info(f"Resumable Upload - Version: {version}, Session: upload_session_{session_id}, "
                     f"File Length: {file_length}, File Type: {file_type}")
        return jsonify({'h': mock.generate_file_handle(session_id, file_type)}), 200

    @app.route('/v<version>/<phone_number_id>/message_templates', methods=['POST', 'GET'])
    def message_templates(version, phone_number_id):
        if not mock.validate_bearer_token(request):
            return jsonify(*mock.oauth_error(
                'Invalid OAuth access token. Failed at endpoint /v<version>/<phone_number_id>/message_templates'
            ))
        if request.method == 'POST':
            template = mock.create_template(request.get_json())
            logger.info(f"Create Message Template - Version: {version}, Phone ID: {phone_number_id}")
            return jsonify({
                'id': template['id'],
                'status': 'APPROVED',
                **mock.paged_response([template])
            }), 200
        if request.method == 'GET':
            logger.info(f"Get Message Templates - Version: {version}, Phone ID: {phone_number_id}")
            templates = mock.load_templates()
            return jsonify(mock.paged_response(templates)), 200

    @app.route('/v<version>/<template_id>', methods=['GET', 'POST'])
    def template_by_id(version, template_id):
        if not mock.validate_bearer_token(request):
            return jsonify(*mock.oauth_error())
        if request.method == 'POST':
            data = request.get_json()
            mock.update_template(template_id, data)
            logger.info(f"Update Template - Version: {version}, Template ID: {template_id}")
            return jsonify({'success': True}), 200
        if request.method == 'GET':
            logger.info(f"Get Template By ID - Version: {version}, Template ID: {template_id}")
            template = mock.get_or_create_template(template_id)
            return jsonify(template), 200

    @app.route('/set-odoo-whatsapp-webhook-account-1', methods=['POST'])
    def set_odoo_whatsapp_webhook_account_1():
        data = request.json
        config.MOCK_WEBHOOK_TOKEN_1 = data.get('webhook_token')
        logger.info(f"Updated webhook token to: {config.MOCK_WEBHOOK_TOKEN_1}")
        return jsonify(data)

    @app.route('/set-odoo-whatsapp-webhook-account-2', methods=['POST'])
    def set_odoo_whatsapp_webhook_account_2():
        data = request.json
        config.MOCK_WEBHOOK_TOKEN_2 = data.get('webhook_token')
        logger.info(f"Updated webhook token to: {config.MOCK_WEBHOOK_TOKEN_2}")
        return jsonify(data)

    @app.route('/send-manual-webhook-message', methods=['POST'])
    def send_manual_webhook():
        data = request.json
        account = data.get('account_type', False)
        acct = mock.get_account_config(account)

        phone_number_id = acct['phone_number_id']
        app_secret = acct['app_secret']
        waba_id = acct['waba_id']
        webhook_url = config.MOCK_WEBHOOK_URL

        from_number = data.get('from_phone_number')
        message_text = data.get('message')
        parent_msg_id = data.get('parent_msg_id', False)

        logger.info(f"Manual message request - From: {from_number}, To webhook: {webhook_url}")
        if not all([webhook_url, phone_number_id, from_number, message_text]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        message = {
            "from": from_number,
            "id": f"wamid.manual_{random.randint(1000000, 9999999)}",
            "timestamp": str(int(time.time())),
            "text": {"body": message_text},
            "type": "text"
        }
        if parent_msg_id:
            message['context'] = {'id': parent_msg_id}

        values = {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": phone_number_id,
                "phone_number_id": phone_number_id
            },
            "contacts": [{"profile": {"name": "Dashboard User"}, "wa_id": from_number}],
            "messages": [message]
        }

        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": waba_id if waba_id else phone_number_id,
                "changes": [{"value": values, "field": "messages"}]
            }]
        }

        headers = {'Content-Type': 'application/json'}
        payload_bytes = json.dumps(webhook_payload, separators=(',', ':')).encode('utf-8')

        if app_secret:
            signature = hmac.new(
                app_secret.encode('utf-8'),
                msg=payload_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()
            headers['X-Hub-Signature-256'] = f'sha256={signature}'
            logger.info(f"Generated X-Hub-Signature-256: sha256={signature}")
            logger.info(f"Payload bytes length: {len(payload_bytes)}")
        else:
            logger.warning("No app_secret provided, skipping signature generation")

        try:
            import requests
            response = requests.post(webhook_url, data=payload_bytes, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Manual message sent successfully to {webhook_url}")
            return jsonify({
                'success': True,
                'message': 'Message sent successfully',
                'signature_included': bool(app_secret)
            }), 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send manual message: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/v<version>/<phone_number_id>/messages', methods=['POST'])
    def send_message(version, phone_number_id):
        """Mock endpoint for sending WhatsApp messages via Graph API"""
        data = request.get_json()
        logger.info(f"Send Message Request - Version: {version}, Phone ID: {phone_number_id}")
        logger.info(f"Message Data: {data}")
        to_number = data.get('to', '')
        return jsonify({
            'messaging_product': 'whatsapp',
            'contacts': [{'input': to_number, 'wa_id': to_number}],
            'messages': [{'id': f'mock_message_id_{random.randint(10000, 99999)}'}]
        }), 200
