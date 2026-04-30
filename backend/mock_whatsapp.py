import json
import os
import random
import base64
import time
import logging

from configs import config

logger = logging.getLogger(__name__)

TEMPLATES_PATH = os.path.join(config.ROOT_DIR, "mock_data/message_templates.json")


class MockWhatsApp:
    
    # ── Auth ──────────────────────────────────────────────────────────

    VALID_TOKENS = {config.MOCK_ACCESS_TOKEN_1, config.MOCK_ACCESS_TOKEN_2}
    VALID_PHONE_IDS = {config.MOCK_PHONE_NUMBER_ID_1, config.MOCK_PHONE_NUMBER_ID_2}

    @staticmethod
    def extract_bearer_token(request):
        """Extract the Bearer token from the Authorization header."""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header.replace('Bearer ', '', 1)
        return None

    @classmethod
    def validate_bearer_token(cls, request):
        """Return the token if valid, None otherwise."""
        token = cls.extract_bearer_token(request)
        if token in cls.VALID_TOKENS:
            return token
        return None

    @classmethod
    def validate_access_token_param(cls, request):
        """Validate access_token from query params. Return token if valid, None otherwise."""
        token = request.args.get('access_token')
        if token in cls.VALID_TOKENS:
            return token
        return None

    @classmethod
    def is_valid_phone_id(cls, phone_number_id):
        return phone_number_id in cls.VALID_PHONE_IDS

    # ── Error responses ───────────────────────────────────────────────

    @staticmethod
    def oauth_error(message='Invalid OAuth access token.', code=190):
        return {
            'error': {
                'message': message,
                'type': 'OAuthException',
                'code': code,
                'fbtrace_id': 'mock_trace_id'
            }
        }, 401

    @staticmethod
    def not_found_error(message='Resource not found.'):
        return {
            'error': {
                'message': message,
                'type': 'OAuthException',
                'code': 100,
                'fbtrace_id': 'mock_trace_id'
            }
        }, 404

    # ── Template storage ──────────────────────────────────────────────

    @staticmethod
    def load_templates():
        """Read all templates from the JSON file."""
        try:
            with open(TEMPLATES_PATH, "r") as f:
                return json.loads(f.read() or "[]")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            return []

    @staticmethod
    def save_templates(templates):
        """Write the full template list back to the JSON file."""
        try:
            with open(TEMPLATES_PATH, "w") as f:
                json.dump(templates, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving templates: {e}")

    @classmethod
    def get_template_by_id(cls, template_id):
        """Return a single template dict or None."""
        for t in cls.load_templates():
            if t.get('id') == template_id:
                return t
        return None

    @classmethod
    def get_or_create_template(cls, template_id):
        """Return an existing template or create a fallback and persist it."""
        templates = cls.load_templates()
        for t in templates:
            if t.get('id') == template_id:
                return t
        # Not found — create, save, and return
        template = {
            'id': template_id,
            'name': 'unknown_template',
            'components': [],
            'language': 'en_US',
            'status': 'APPROVED',
            'category': 'UTILITY',
            'quality_score': {'score': 'unknown'},
        }
        templates.append(template)
        cls.save_templates(templates)
        logger.info(f"Template {template_id} not found — created and saved fallback")
        return template

    @classmethod
    def create_template(cls, data):
        """Create a new template from request data and persist it. Returns the template dict."""
        language = data.get('language', 'en')
        template = {
            'name': data.get('name', 'unnamed_template'),
            'components': data.get('components', []),
            'language': language if '_' in language else f"{language}_US",
            'status': 'APPROVED',
            'category': data.get('category', 'MARKETING'),
            'id': str(random.randint(1000000000000000, 9999999999999999)),
            'quality_score': {'score': 'unknown'},
        }
        templates = cls.load_templates()
        templates.append(template)
        cls.save_templates(templates)
        return template

    @classmethod
    def update_template(cls, template_id, data):
        """Update an existing template or create it if not found. Returns the template dict."""
        templates = cls.load_templates()
        components = data.get('components', [])
        category = data.get('category')

        for t in templates:
            if t.get('id') == template_id:
                if components:
                    t['components'] = components
                if category:
                    t['category'] = category
                t['status'] = 'APPROVED'
                cls.save_templates(templates)
                return t

        # Template not found — create it with the given ID
        template = {
            'id': template_id,
            'name': data.get('name', 'unnamed_template'),
            'components': components,
            'language': data.get('language', 'en_US'),
            'status': 'APPROVED',
            'category': category or 'UTILITY',
            'quality_score': {'score': 'unknown'},
        }
        templates.append(template)
        cls.save_templates(templates)
        return template

    # ── Upload helpers ────────────────────────────────────────────────

    @staticmethod
    def generate_upload_session_id():
        return f'upload_session_{random.randint(1000000000, 9999999999)}'

    @staticmethod
    def generate_file_handle(session_id, file_type):
        handle_data = f"upload_session_{session_id}:{file_type}:{int(time.time())}"
        return f"4:{base64.b64encode(handle_data.encode()).decode()}::{file_type}:ARZ_mock_handle_{session_id}"

    # ── Account config lookup ─────────────────────────────────────────

    @staticmethod
    def get_account_config(account_type):
        """Return a dict of config values for the given account ('account_1' or 'account_2')."""
        is_one = account_type == 'account_1'
        return {
            'phone_number_id': config.MOCK_PHONE_NUMBER_ID_1 if is_one else config.MOCK_PHONE_NUMBER_ID_2,
            'access_token': config.MOCK_ACCESS_TOKEN_1 if is_one else config.MOCK_ACCESS_TOKEN_2,
            'webhook_token': config.MOCK_WEBHOOK_TOKEN_1 if is_one else config.MOCK_WEBHOOK_TOKEN_2,
            'app_secret': config.MOCK_APP_SECRET_1 if is_one else config.MOCK_APP_SECRET_2,
            'app_id': config.MOCK_APP_ID_1 if is_one else config.MOCK_APP_ID_2,
            'waba_id': config.MOCK_WABA_ID_1 if is_one else config.MOCK_WABA_ID_2,
        }

    # ── Paging wrapper ────────────────────────────────────────────────

    @staticmethod
    def paged_response(data):
        return {
            'data': data,
            'paging': {
                'cursors': {
                    'before': 'MAZDZD',
                    'after': 'MjQZD'
                }
            }
        }
