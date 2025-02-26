import os
import logging
from config import CACHE_DIR

# Configure logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def ensure_cache_dir():
    """Ensure that the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
            logger.info(f"Cache directory created at {CACHE_DIR}")
        except Exception:
            logger.exception("Failed to create cache directory.")

def cleanup_file(filepath):
    """Delete the given file and remove the cache directory if empty."""
    try:
        os.remove(filepath)
        logger.info(f"Removed file {filepath}")
        if os.path.exists(CACHE_DIR) and not os.listdir(CACHE_DIR):
            os.rmdir(CACHE_DIR)
            logger.info(f"Removed empty cache directory {CACHE_DIR}")
    except Exception:
        logger.exception("Error cleaning up file")
        
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    from config import ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS