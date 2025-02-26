import os
from decouple import config

# Maximum allowed content length for uploads (in bytes; e.g., 5MB)
MAX_CONTENT_LENGTH = int(config("MAX_CONTENT_LENGTH", default=5 * 1024 * 1024))

# Allowed file extensions for uploaded images
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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