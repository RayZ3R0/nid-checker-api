import os
import secrets
from decouple import config

# Authentication settings
SECRET_KEY = config("SECRET_KEY", default=secrets.token_hex(32))
AUTH_TOKEN = config("AUTH_TOKEN", default=secrets.token_hex(16))
TOKEN_HEADER_NAME = "X-API-Token"

# Security settings
RATE_LIMIT = int(config("RATE_LIMIT", default=10))  # requests per minute
RATE_LIMIT_WINDOW = int(config("RATE_LIMIT_WINDOW", default=60))  # seconds

# Maximum allowed content length for uploads (in bytes; e.g., 5MB)
MAX_CONTENT_LENGTH = int(config("MAX_CONTENT_LENGTH", default=5 * 1024 * 1024))

# Allowed file extensions for uploaded images
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Allowed MIME types for additional validation
ALLOWED_MIME_TYPES = set(['image/png', 'image/jpeg', 'image/jpg'])

# Cache directory
CACHE_DIR = config("CACHE_DIR", default="cache")

# OCR parameters (you can add more tuning parameters here)
OCR_PARAMS = {
    "beamWidth": int(config("OCR_BEAM_WIDTH", default=5)),
    "contrast_ths": float(config("OCR_CONTRAST_THS", default=0.1)),
    "adjust_contrast": float(config("OCR_ADJUST_CONTRAST", default=0.5)),
    "text_threshold": float(config("OCR_TEXT_THRESHOLD", default=0.7)),
    "low_text": float(config("OCR_LOW_TEXT", default=0.4)),
    "link_threshold": float(config("OCR_LINK_THRESHOLD", default=0.4))
}

# Security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self'",
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Cache-Control': 'no-store, no-cache'
}