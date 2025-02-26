from flask import Flask, request, jsonify, render_template_string, send_from_directory
import cv2
import numpy as np
import os
import re
import easyocr
import time

app = Flask(__name__)

# Initialize EasyOCR with optimal settings
reader = easyocr.Reader(
    ['en'], 
    gpu=False,  # Change to True if you have a GPU
    model_storage_directory='model',
    download_enabled=True,
    recog_network='english_g2'  # Using the best model for English
)

def extract_nid_fields(image):
    """Extract NID fields using direct EasyOCR capabilities"""
    # Dictionary to store results
    nid_data = {
        'name': '',
        'date_of_birth': '',
        'id_number': ''
    }
    
    # Start timing
    start_time = time.time()
    
    # Use EasyOCR directly on the image with optimal parameters
    results = reader.readtext(
        image,
        paragraph=True,  # Group text by paragraphs
        detail=1,        # Include bounding boxes 
        decoder='greedy',
        beamWidth=5,
        contrast_ths=0.1,
        adjust_contrast=0.5,
        text_threshold=0.7,
        low_text=0.4,
        link_threshold=0.4,
    )
    
    end_time = time.time()
    
    # Extract text from results
    text_blocks = []
    for result in results:
        # EasyOCR returns [bounding_box, text, confidence]
        # Handle different result formats safely
        try:
            if len(result) >= 2:  # As long as we have bbox and text
                text = result[1]
                text_blocks.append(text)
        except Exception as e:
            print(f"Error processing result: {e}")
            continue
    
    # Join all text blocks
    all_text = "\n".join(text_blocks)
    
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
    
    # Processing info
    processing_info = {
        'time_taken': f"{(end_time - start_time):.2f} seconds",
        'model': 'english_g2'
    }
    
    return nid_data, all_text, processing_info

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image_file.save('uploaded_image.jpg')

    # Load image
    image = cv2.imread('uploaded_image.jpg')
    nid_data, _, _ = extract_nid_fields(image)

    return jsonify(nid_data)

@app.route('/')
def test_page():
    # Path to test image
    test_image_path = os.path.join('testimages', 'image.png')
    
    # Process the image
    image = cv2.imread(test_image_path)
    
    # Handle case where image might not be found
    if image is None:
        html = '''
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error: Test image not found</h1>
            <p>Please make sure you have an image named "image.png" in the testimages directory.</p>
        </body>
        </html>
        '''
        return render_template_string(html)
    
    # Extract data using direct EasyOCR
    nid_data, all_text, processing_info = extract_nid_fields(image)
    
    # Create HTML to display results
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NID Card OCR</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; color: #333; }
            h1 { color: #2c3e50; }
            .container { display: flex; flex-direction: column; gap: 20px; max-width: 1200px; margin: 0 auto; }
            .row { display: flex; gap: 20px; margin-bottom: 20px; }
            .image-container { flex: 1; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; border-radius: 8px; }
            .text-container { flex: 1; border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #f9f9f9; }
            img { max-width: 100%; border-radius: 4px; }
            pre { white-space: pre-wrap; background-color: #f4f6f8; padding: 15px; border-radius: 4px; font-size: 14px; }
            .field { margin-bottom: 15px; padding: 15px; background-color: #e8f4f8; border-radius: 8px; border-left: 4px solid #3498db; }
            .field-name { font-weight: bold; color: #2980b9; margin-bottom: 5px; }
            .field-value { font-family: monospace; font-size: 1.2em; background-color: #fff; padding: 8px; border-radius: 4px; }
            .info { font-style: italic; margin-top: 15px; color: #7f8c8d; display: flex; justify-content: space-between; }
            .badge { background-color: #3498db; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>🔎 NID Card OCR Results</h1>
        <div class="container">
            <div class="row">
                <div class="image-container">
                    <h2>📷 Original Image</h2>
                    <img src="/testimages/image.png" alt="NID Card">
                </div>
                <div class="text-container">
                    <h2>📝 Raw Extracted Text</h2>
                    <pre>{{ all_text }}</pre>
                    <div class="info">
                        <span>Model: <span class="badge">{{ processing_info.model }}</span></span>
                        <span>Processing time: {{ processing_info.time_taken }}</span>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; border-top: 4px solid #2ecc71;">
                <h2>🎯 Extracted Information</h2>
                <div class="field">
                    <div class="field-name">👤 Name:</div>
                    <div class="field-value">{{ nid_data.name or "Not detected" }}</div>
                </div>
                
                <div class="field">
                    <div class="field-name">🎂 Date of Birth:</div>
                    <div class="field-value">{{ nid_data.date_of_birth or "Not detected" }}</div>
                </div>
                
                <div class="field">
                    <div class="field-name">🆔 ID Number:</div>
                    <div class="field-value">{{ nid_data.id_number or "Not detected" }}</div>
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
    # Create testimages directory if it doesn't exist
    if not os.path.exists('testimages'):
        os.makedirs('testimages')
    
    app.run(debug=True, host='0.0.0.0')