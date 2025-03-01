import os
import cv2
import difflib
import logging
import uuid
from flask import Flask, request, jsonify, g, after_this_request
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile
from nid_extractor import extract_nid_fields
from utils import (
    ensure_cache_dir, 
    cleanup_file, 
    allowed_file, 
    validate_file_mime, 
    authenticate, 
    rate_limit, 
    handle_exceptions,
    CACHE_DIR
)
from config import MAX_CONTENT_LENGTH, SECURITY_HEADERS

# Configure app-level logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Apply security headers to all responses
@app.after_request
def set_security_headers(response):
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "File too large"}), 413

@app.route('/', methods=['GET'])
@handle_exceptions
def index():
    return jsonify({"message": "NID Extractor API is running."})

@app.route('/process_image', methods=['POST'])
@authenticate
@rate_limit
@handle_exceptions
def process_image():
    """
    Process an uploaded image, parse extra data, and return the extracted
    information along with similarity ratings. Adds:
      - Granular error handling
      - Security via file validation
      - Token authentication
      - Rate limiting
      - Resource management with a temporary file in the configured cache directory
    """
    # Generate a request ID for traceability
    request_id = str(uuid.uuid4())
    logger.info(f"Request {request_id}: Processing new image")
    
    # Validate that an image file was provided.
    if 'image' not in request.files:
        logger.warning(f"Request {request_id}: No image provided")
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == "":
        logger.warning(f"Request {request_id}: Empty filename")
        return jsonify({'error': 'Empty filename'}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        logger.warning(f"Request {request_id}: File type not allowed")
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Ensure cache directory exists
    try:
        ensure_cache_dir()
    except Exception as e:
        logger.error(f"Request {request_id}: Cache directory error - {str(e)}")
        return jsonify({'error': 'Server configuration error'}), 500
    
    # Create a temporary file in the cache directory with a secure random name
    try:
        with NamedTemporaryFile(dir=CACHE_DIR, suffix=".jpg", delete=False) as temp:
            image_path = temp.name
            file.save(image_path)
            logger.info(f"Request {request_id}: Saved uploaded image to {image_path}")
    except Exception as e:
        logger.exception(f"Request {request_id}: Failed to save uploaded image - {str(e)}")
        return jsonify({'error': 'Failed to process image upload'}), 500

    # Double-check file type with MIME validation
    if not validate_file_mime(image_path):
        logger.warning(f"Request {request_id}: Invalid MIME type")
        cleanup_file(image_path)
        return jsonify({'error': 'Invalid file format'}), 400

    # Open the image using OpenCV
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Request {request_id}: Failed to read image using OpenCV")
            cleanup_file(image_path)
            return jsonify({'error': 'Invalid image provided'}), 400
    except Exception as e:
        logger.exception(f"Request {request_id}: OpenCV error - {str(e)}")
        cleanup_file(image_path)
        return jsonify({'error': 'Image processing error'}), 500

    # Extract NID fields
    try:
        result = extract_nid_fields(image)
    except Exception as e:
        logger.exception(f"Request {request_id}: OCR extraction error - {str(e)}")
        cleanup_file(image_path)
        return jsonify({'error': 'OCR processing failed'}), 500

    # Retrieve extra data sent with the form
    try:
        provided_name = request.form.get("Name", "").strip()
        provided_dob = request.form.get("Date of Birth", "").strip()
    except Exception as e:
        logger.exception(f"Request {request_id}: Form data parsing error - {str(e)}")
        provided_name = ""
        provided_dob = ""

    # Initialize similarity dictionary
    try:
        if not provided_name and not provided_dob:
            # No comparison data provided at all
            similarity = {"status": "no_comparison_data_provided"}
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
    except Exception as e:
        logger.exception(f"Request {request_id}: Error calculating similarity - {str(e)}")
        result["similarity"] = {"status": "error_calculating_similarity"}

    # Clean up the temporary file
    cleanup_file(image_path)
    
    logger.info(f"Request {request_id}: Processing complete")
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')  # Set debug to False in production