from flask import Flask, request, jsonify, render_template_string, send_from_directory
import cv2
import numpy as np
import os
import re
import easyocr
import time

app = Flask(__name__)
# Initialize EasyOCR with advanced settings
reader = easyocr.Reader(
    ['en'], 
    gpu=False,  # Set to False if you don't have a GPU
    model_storage_directory='model',
    download_enabled=True,
    quantize=False,  # Better accuracy but slower
    recog_network='english_g2'  # This is the "engine2" equivalent - more accurate model
)

def preprocess_for_easyocr(image):
    """Apply enhanced preprocessing for better EasyOCR results"""
    # Copy the original image
    original = image.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter - preserves edges while reducing noise
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(bilateral)
    
    # Apply slight sharpening
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    return sharpened

def extract_nid_fields(image):
    """Extract NID fields using optimized EasyOCR"""
    # Make a copy of the original image
    original = image.copy()
    
    # Dictionary to store results
    nid_data = {
        'name': '',
        'date_of_birth': '',
        'id_number': ''
    }
    
    # Enhanced preprocessing
    preprocessed = preprocess_for_easyocr(original)
    
    # Run EasyOCR with advanced parameters
    # paragraph=True groups text by paragraph
    # detail=1 provides bounding box info too
    # batch_size=1 for consistent behavior
    # Set a minimum confidence threshold
    start_time = time.time()
    results = reader.readtext(
        preprocessed,
        paragraph=True,
        detail=1,
        batch_size=1,
        min_size=10,
        slope_ths=0.2,
        ycenter_ths=0.7,
        height_ths=0.6,
        width_ths=0.8,
        decoder='beamsearch',
        beamWidth=5
    )
    end_time = time.time()
    
    # Extract text and confidence
    text_blocks = []
    for (bbox, text, prob) in results:
        # Only include text with reasonable confidence
        if prob > 0.2:  # Adjust threshold as needed
            text_blocks.append(text)
    
    all_text = "\n".join(text_blocks)
    
    # Store visualization data
    region_images = {
        'preprocessed': preprocessed
    }
    
    # Extract name - look for name patterns
    name_patterns = [
        r"Name[:\s]+([A-Za-z\s]+)",
        r"(?:^|\n)([A-Z][A-Z\s]+)(?:\n|$)",
        r"([A-Z][A-Z\s]+)(?=\s+(?:Date|Birth|DOB))"  # Name typically appears before DOB
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, all_text)
        if name_match:
            nid_data['name'] = name_match.group(1).strip()
            break
    
    # Extract date of birth with more comprehensive patterns
    dob_patterns = [
        r"(?:Date of Birth|DOB|Birth)[:\s]+(\d{1,2}[\s-]*[A-Za-z]+[\s-]*\d{4})",
        r"(?:Date of Birth|DOB|Birth)[:\s]+(\d{1,2}[\s/-]*\d{1,2}[\s/-]*\d{2,4})",
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"  # Common date formats like DD/MM/YYYY
    ]
    
    for pattern in dob_patterns:
        dob_match = re.search(pattern, all_text, re.IGNORECASE)
        if dob_match:
            nid_data['date_of_birth'] = dob_match.group(1).strip()
            break
    
    # Extract ID number with more specific Bangladesh NID patterns
    id_patterns = [
        r"(?:ID|Number|No|NID)[:\s]+(\d[\d\s]+\d)",
        r"(\d{10,})",  # Sequence of 10+ digits
        r"(?:^|\n)(\d[\d\s]+\d)(?:\n|$)",  # Digit sequence on its own line
        r"(\d{3}[\s-]*\d{3}[\s-]*\d{4})"   # Common BD NID format: XXX XXX XXXX
    ]
    
    for pattern in id_patterns:
        id_match = re.search(pattern, all_text)
        if id_match:
            id_text = id_match.group(1)
            nid_data['id_number'] = re.sub(r'\s', '', id_text)
            break
    
    # Add processing time info
    processing_info = {
        'time_taken': f"{(end_time - start_time):.2f} seconds",
        'model': 'english_g2'
    }
    
    return nid_data, region_images, all_text, processing_info

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image_file.save('uploaded_image.jpg')

    # Load image
    image = cv2.imread('uploaded_image.jpg')
    nid_data, _, _, _ = extract_nid_fields(image)

    return jsonify(nid_data)

@app.route('/')
def test_page():
    # Path to test image
    test_image_path = os.path.join('testimages', 'image.png')
    
    # Process the image
    image = cv2.imread(test_image_path)
    
    # Extract data using optimized EasyOCR
    nid_data, region_images, all_text, processing_info = extract_nid_fields(image)
    
    # Save the preprocessed image for display
    preprocessed_path = os.path.join('testimages', 'preprocessed_image.png')
    cv2.imwrite(preprocessed_path, region_images['preprocessed'])
    
    # Create HTML to display results
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NID OCR Test with Advanced EasyOCR</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .container { display: flex; flex-direction: column; gap: 20px; }
            .row { display: flex; gap: 20px; margin-bottom: 20px; }
            .image-container { flex: 1; }
            .text-container { flex: 1; border: 1px solid #ccc; padding: 15px; border-radius: 5px; }
            img { max-width: 100%; border: 1px solid #ddd; }
            pre { white-space: pre-wrap; }
            .comparison { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
            .field { margin-bottom: 10px; padding: 10px; background-color: #e9ecef; border-radius: 5px; }
            .field-name { font-weight: bold; color: #495057; }
            .field-value { font-family: monospace; font-size: 1.1em; }
            .info { color: #6c757d; font-style: italic; margin-top: 15px; }
        </style>
    </head>
    <body>
        <h1>NID OCR Test with Advanced EasyOCR</h1>
        <div class="container">
            <div class="row">
                <div class="image-container">
                    <h2>Original Image</h2>
                    <img src="/testimages/image.png" alt="Test NID Card">
                </div>
                <div class="image-container">
                    <h2>Preprocessed Image</h2>
                    <img src="/testimages/preprocessed_image.png" alt="Preprocessed Image">
                </div>
            </div>
            
            <div class="text-container">
                <h2>Extracted Text (EasyOCR)</h2>
                <pre>{{ all_text }}</pre>
                <div class="info">
                    <p>Model: {{ processing_info.model }}</p>
                    <p>Processing time: {{ processing_info.time_taken }}</p>
                </div>
            </div>
            
            <div class="comparison">
                <h2>Extracted Fields</h2>
                <div class="field">
                    <span class="field-name">Name:</span>
                    <div class="field-value">{{ nid_data.name }}</div>
                </div>
                
                <div class="field">
                    <span class="field-name">Date of Birth:</span>
                    <div class="field-value">{{ nid_data.date_of_birth }}</div>
                </div>
                
                <div class="field">
                    <span class="field-name">ID Number:</span>
                    <div class="field-value">{{ nid_data.id_number }}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, all_text=all_text, nid_data=nid_data, processing_info=processing_info)

# Serve static files from testimages directory
@app.route('/testimages/<path:filename>')
def serve_image(filename):
    return send_from_directory('testimages', filename)

if __name__ == '__main__':
    if not os.path.exists('testimages'):
        os.makedirs('testimages')
    
    app.run(debug=True, host='0.0.0.0')