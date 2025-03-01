import os
import time
import logging
import magic
import functools
from werkzeug.exceptions import RequestEntityTooLarge, Unauthorized, TooManyRequests
from flask import request, jsonify, current_app, g
from config import CACHE_DIR, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, AUTH_TOKEN, TOKEN_HEADER_NAME, RATE_LIMIT, RATE_LIMIT_WINDOW

# Configure logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Store for rate limiting
request_history = {}

def ensure_cache_dir():
    """Ensure that the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR, mode=0o750)  # More secure permissions
            logger.info(f"Cache directory created at {CACHE_DIR}")
        except Exception as e:
            logger.exception("Failed to create cache directory: %s", str(e))
            raise

def cleanup_file(filepath):
    """Delete the given file and remove the cache directory if empty."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Removed file {filepath}")
            if os.path.exists(CACHE_DIR) and not os.listdir(CACHE_DIR):
                os.rmdir(CACHE_DIR)
                logger.info(f"Removed empty cache directory {CACHE_DIR}")
    except Exception as e:
        logger.exception("Error cleaning up file: %s", str(e))

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_mime(file_path):
    """Validate file MIME type using python-magic."""
    try:
        mime = magic.Magic(mime=True)
        file_mime = mime.from_file(file_path)
        return file_mime in ALLOWED_MIME_TYPES
    except Exception as e:
        logger.exception("Error validating file MIME type: %s", str(e))
        return False

def authenticate(f):
    """Decorator for token authentication."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get(TOKEN_HEADER_NAME)
        print(f"DEBUG: Received token: {token}")
        print(f"DEBUG: Expected token: {AUTH_TOKEN}")
        print(f"DEBUG: Header name: {TOKEN_HEADER_NAME}")
        
        if not token:
            logger.warning("Authentication failed: No token provided")
            return jsonify({"error": "Authentication required"}), 401
        
        if token != AUTH_TOKEN:
            logger.warning("Authentication failed: Invalid token")
            return jsonify({"error": "Invalid authentication token"}), 401
        
        return f(*args, **kwargs)
    return decorated

def rate_limit(f):
    """Decorator for rate limiting."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # Get client identifier (IP address or better yet, the token)
        client_id = request.headers.get(TOKEN_HEADER_NAME, request.remote_addr)
        current_time = time.time()
        
        # Clean old entries
        for key in list(request_history.keys()):
            request_history[key] = [t for t in request_history.get(key, []) 
                                    if current_time - t < RATE_LIMIT_WINDOW]
        
        # Check rate limit
        client_history = request_history.get(client_id, [])
        if len(client_history) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        # Update history
        client_history.append(current_time)
        request_history[client_id] = client_history
        
        return f(*args, **kwargs)
    return decorated

def handle_exceptions(f):
    """Decorator for exception handling."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except RequestEntityTooLarge:
            logger.warning("File too large")
            return jsonify({"error": "Uploaded file exceeds size limit"}), 413
        except Unauthorized:
            return jsonify({"error": "Authentication required"}), 401
        except TooManyRequests:
            return jsonify({"error": "Rate limit exceeded"}), 429
        except Exception as e:
            logger.exception("Unexpected error: %s", str(e))
            return jsonify({"error": "Internal server error"}), 500
    return decorated