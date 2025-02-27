import os
from celery import Celery
from nid_extractor import extract_nid_fields
import cv2
from decouple import config

# Configure Celery
redis_url = config('REDIS_URL', default='redis://localhost:6379/0')
celery_app = Celery('nid_extractor', broker=redis_url, backend=redis_url)

@celery_app.task
def process_image_async(image_path):
    """
    Asynchronously process an image and extract NID fields
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        
        # Process the image
        result = extract_nid_fields(image)
        
        # Clean up temporary file
        try:
            os.remove(image_path)
        except:
            pass
            
        return result
        
    except Exception as e:
        return {"error": str(e)}