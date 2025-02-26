import os
import cv2
import difflib
from flask import Flask, request, jsonify
from nid_extractor import extract_nid_fields
from utils import ensure_cache_dir, cleanup_file

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return jsonify({"message": "NID Extractor API is running."})

@app.route('/process_image', methods=['POST'])
def process_image():
    """Process uploaded image, parse extra data, and return extracted info with similarity ratings."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Ensure the cache directory exists.
    ensure_cache_dir()
    
    # Save the uploaded image to the cache directory.
    image_file = request.files['image']
    image_path = os.path.join("cache", "uploaded_image.jpg")
    image_file.save(image_path)
    
    # Open the image.
    image = cv2.imread(image_path)
    
    # Extract NID fields from the image.
    result = extract_nid_fields(image)
    
    # Get additional data sent in the form.
    provided_name = request.form.get("Name", "").strip()
    provided_dob = request.form.get("Date of Birth", "").strip()
    
    # Initialize similarity ratings.
    similarity = {"name_similarity": None, "dob_similarity": None}
    
    # Compute similarity for Name using difflib.
    extracted_name = result.get("Name", "").strip()
    if provided_name and extracted_name:
        similarity["name_similarity"] = round(
            difflib.SequenceMatcher(None, provided_name.upper(), extracted_name.upper()).ratio(), 2)
    
    # Compute similarity for Date of Birth.
    extracted_dob = result.get("Date of birth", "").strip()
    if provided_dob and extracted_dob:
        similarity["dob_similarity"] = round(
            difflib.SequenceMatcher(None, provided_dob.upper(), extracted_dob.upper()).ratio(), 2)
    
    # Add similarity rating to the response.
    result["similarity"] = similarity
    
    # Clean up: delete the cached image and remove the cache directory if empty.
    cleanup_file(image_path)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')