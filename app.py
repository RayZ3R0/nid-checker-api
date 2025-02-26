import os
import cv2
import difflib
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile
from nid_extractor import extract_nid_fields
from utils import ensure_cache_dir, cleanup_file, allowed_file, CACHE_DIR
from config import MAX_CONTENT_LENGTH

# Configure app-level logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "NID Extractor API is running."})

@app.route('/process_image', methods=['POST'])
def process_image():
    """
    Process an uploaded image, parse extra data, and return the extracted
    information along with similarity ratings. Adds:
      - Granular error handling
      - Security via file validation
      - Resource management with a temporary file in the configured cache directory
      - Placeholders/comments for asynchronous processing for heavy OCR tasks
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

    # Open the image using OpenCV.
    image = cv2.imread(image_path)
    if image is None:
        logger.error("Failed to read image using OpenCV.")
        cleanup_file(image_path)
        return jsonify({'error': 'Invalid image provided'}), 400

    # For high loads, consider submitting OCR to a worker (e.g., Celery).
    try:
        result = extract_nid_fields(image)
    except Exception:
        logger.exception("Error during OCR extraction")
        cleanup_file(image_path)
        return jsonify({'error': 'OCR processing failed'}), 500

    # Retrieve extra data sent with the form.
    provided_name = request.form.get("Name", "").strip()
    provided_dob = request.form.get("Date of Birth", "").strip()

    similarity = {"name_similarity": None, "dob_similarity": None}
    
    extracted_name = result.get("Name", "").strip()
    if provided_name and extracted_name:
        similarity["name_similarity"] = round(
            difflib.SequenceMatcher(None, provided_name.upper(), extracted_name.upper()).ratio(), 2)
    
    extracted_dob = result.get("Date of birth", "").strip()
    if provided_dob and extracted_dob:
        similarity["dob_similarity"] = round(
            difflib.SequenceMatcher(None, provided_dob.upper(), extracted_dob.upper()).ratio(), 2)
    
    result["similarity"] = similarity

    # Clean up the temporary file.
    cleanup_file(image_path)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')