import os

# Define a cache directory constant.
CACHE_DIR = "cache"

def ensure_cache_dir():
    """Ensure that the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def cleanup_file(filepath):
    """Delete the given file and remove the cache directory if empty."""
    try:
        os.remove(filepath)
        # If the cache folder is empty, remove it.
        if not os.listdir(CACHE_DIR):
            os.rmdir(CACHE_DIR)
    except Exception as e:
        print(f"Error cleaning up file: {e}")