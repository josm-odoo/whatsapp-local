from flask import Flask, request
import logging
from datetime import datetime
from collections import deque

from frontend import register_frontend_routes
from backend.routes import register_backend_routes, register_backend_routes

from flask_socketio import SocketIO, emit

# Import our modules
# from dashboard.dashboard import create_dashboard_route
# from webhook.routes import register_backend_routes

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Filter to suppress werkzeug logs for /traffic-logs endpoint
class TrafficLogsFilter(logging.Filter):
    def filter(self, record):
        return '/traffic-logs' not in record.getMessage()

# Apply filter to werkzeug logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(TrafficLogsFilter())

# Store traffic data (last 100 requests)
traffic_log = deque(maxlen=100)

@app.before_request
def log_request():
    """Log all incoming requests for debugging"""
    # Skip logging for /web endpoint to avoid recursion
    if request.path == '/web':
        return

    # Skip logging for common browser requests (favicon, etc.)
    skip_paths = ['/favicon.ico', '/robots.txt', '/apple-touch-icon']
    if any(request.path.startswith(path) for path in skip_paths):
        return

    # Only log webhook/API traffic (not root/health unless from specific hosts)
    is_webhook = (
        request.path.startswith('/v') or  # WhatsApp API paths
        request.path.startswith('/webhook') or
        request.headers.get('Host') in ['graph.facebook.com', 'api.whatsapp.com','localhost:8569'] or
        request.method in ['POST', 'PUT', 'PATCH', 'DELETE']  # Any non-GET requests are likely API calls
    )

    if not is_webhook:
        # Still log to console but don't store in dashboard
        # logger.info(f"=== Skipped (non-webhook): {request.method} {request.path} ===")
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get request body
    body = None
    if request.data:
        try:
            body = request.data.decode('utf-8')
        except:
            body = str(request.data)

    # Store traffic data
    traffic_entry = {
        'timestamp': timestamp,
        'method': request.method,
        'host': request.headers.get('Host'),
        'path': request.path,
        'url': request.url,
        'headers': dict(request.headers),
        'body': body,
        'query_params': dict(request.args)
    }
    traffic_log.append(traffic_entry)
    socketio.emit('new_traffic_log', traffic_entry)

    # Console logging
    logger.info(f"=== Incoming Request ===")
    logger.info(f"Host: {request.headers.get('Host')}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Full URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    if body:
        logger.info(f"Body: {body}")
    logger.info(f"========================")

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to SocketIO')
    emit('connection_response', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected from SocketIO')

@socketio.on('request_all_traffic_logs')
def handle_request_traffic_logs():
    logger.info('Client requested traffic logs')
    emit('all_traffic_logs', list(traffic_log)[::-1])



## Register all frontend routes
register_frontend_routes(app, traffic_log=traffic_log)
register_backend_routes(app)



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
