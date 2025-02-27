import os
import cv2
import difflib
import logging
import time
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile
from nid_extractor import extract_nid_fields
from utils import ensure_cache_dir, cleanup_file, allowed_file
from config import MAX_CONTENT_LENGTH, CACHE_DIR
from auth import auth  # Import the authentication module
from tasks import process_image_async  # Import the Celery task

# Configure app-level logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Set timeout for waiting on Celery tasks (in seconds)
TASK_TIMEOUT = 15  # Adjust based on your typical processing time

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "NID Extractor API is running."})

@app.route('/process_image', methods=['POST'])
@auth.login_required  # Add authentication requirement
def process_image():
    """
    Process an uploaded image, parse extra data, and return the extracted
    information along with similarity ratings. Uses background processing with timeout.
    """
    # Validate that an image file was provided.
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == "":
        return jsonify({'error': 'Empty filename'}), 400
    
    # Validate file extension.
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Ensure cache directory exists.
    ensure_cache_dir()
    
    # Create a temporary file in the cache directory.
    try:
        with NamedTemporaryFile(dir=CACHE_DIR, suffix=".jpg", delete=False) as temp:
            image_path = temp.name
            file.save(image_path)
            logger.info(f"Saved uploaded image to {image_path}")
    except Exception:
        logger.exception("Failed to save uploaded image.")
        return jsonify({'error': 'Failed to process image upload'}), 500

    # Retrieve extra data sent with the form for later use
    provided_name = request.form.get("Name", "").strip()
    provided_dob = request.form.get("Date of Birth", "").strip()

    # Submit task to Celery worker
    task = process_image_async.delay(image_path)
    logger.info(f"Submitted image processing task: {task.id}")
    
    try:
        # Wait for the task to complete with timeout
        result = task.get(timeout=TASK_TIMEOUT)
        
        # If we get here, the task completed within the timeout
        logger.info(f"Task {task.id} completed within timeout")
        
        # Process similarity ratings
        process_similarity_ratings(result, provided_name, provided_dob)
        
        # Return complete result
        return jsonify(result)
    
    except Exception as e:
        logger.info(f"Task {task.id} not completed within timeout: {str(e)}")
        
        # Return task ID so client can check back
        return jsonify({
            'status': 'processing',
            'task_id': task.id,
            'message': 'Image processing is taking longer than expected. Check back using the task_id.'
        })

@app.route('/check_task/<task_id>', methods=['GET'])
@auth.login_required
def check_task(task_id):
    """
    Check the status of a previously submitted task
    """
    try:
        # Import here to avoid circular imports
        from tasks import celery_app
        
        # Check task status
        task = celery_app.AsyncResult(task_id)
        
        if task.ready():
            # Task is complete, get the result
            result = task.get()
            
            # We don't have the form data here, so we can't calculate similarity
            # The client would need to send that data again if needed
            
            return jsonify({
                'status': 'complete',
                'result': result
            })
        else:
            # Task still processing
            return jsonify({
                'status': 'processing',
                'task_id': task_id,
                'message': 'Image is still being processed. Please check again later.'
            })
            
    except Exception:
        logger.exception(f"Error checking task status for {task_id}")
        return jsonify({
            'status': 'error',
            'message': 'Error checking task status. The task ID may be invalid or expired.'
        }), 400

@app.route('/check_task_with_comparison/<task_id>', methods=['POST'])
@auth.login_required
def check_task_with_comparison(task_id):
    """
    Check the status of a previously submitted task and calculate similarity
    with provided comparison data
    """
    try:
        # Import here to avoid circular imports
        from tasks import celery_app
        
        # Check task status
        task = celery_app.AsyncResult(task_id)
        
        if not task.ready():
            # Task still processing
            return jsonify({
                'status': 'processing',
                'task_id': task_id,
                'message': 'Image is still being processed. Please check again later.'
            })
        
        # Task is complete, get the result
        result = task.get()
        
        # Get comparison data
        provided_name = request.form.get("Name", "").strip()
        provided_dob = request.form.get("Date of Birth", "").strip()
        
        # Process similarity ratings
        process_similarity_ratings(result, provided_name, provided_dob)
        
        return jsonify({
            'status': 'complete',
            'result': result
        })
            
    except Exception:
        logger.exception(f"Error checking task status for {task_id}")
        return jsonify({
            'status': 'error',
            'message': 'Error checking task status. The task ID may be invalid or expired.'
        }), 400

def process_similarity_ratings(result, provided_name, provided_dob):
    """
    Calculate similarity ratings between provided and extracted data
    """
    # Initialize similarity dictionary
    if not provided_name and not provided_dob:
        # No comparison data provided at all
        result["similarity"] = {"status": "no_comparison_data_provided"}
    else:
        similarity = {"status": "partial_comparison", "name_similarity": None, "dob_similarity": None}
        
        # Process name similarity if available
        extracted_name = result.get("Name", "").strip()
        if provided_name and extracted_name:
            similarity["name_similarity"] = round(
                difflib.SequenceMatcher(None, provided_name.upper(), extracted_name.upper()).ratio(), 2)
        elif provided_name:
            similarity["name_similarity"] = "no_extracted_name_available"
            
        # Process DOB similarity if available
        extracted_dob = result.get("Date of birth", "").strip()
        if provided_dob and extracted_dob:
            similarity["dob_similarity"] = round(
                difflib.SequenceMatcher(None, provided_dob.upper(), extracted_dob.upper()).ratio(), 2)
        elif provided_dob:
            similarity["dob_similarity"] = "no_extracted_dob_available"
        
        result["similarity"] = similarity

if __name__ == '__main__':
    # This is only for development
    app.run(debug=False, host='0.0.0.0')