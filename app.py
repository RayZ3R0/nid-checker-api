import os
import cv2
from flask import Flask, request, jsonify, send_from_directory
from nid_extractor import extract_nid_fields

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
    """Process uploaded image and return extracted information."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image_file = request.files['image']
    image_file.save('uploaded_image.jpg')
    image = cv2.imread('uploaded_image.jpg')
    result = extract_nid_fields(image)
    return jsonify(result)

@app.route('/')
def test_endpoint():
    """Test endpoint using an image from the testimages folder."""
    test_image_path = os.path.join('testimages', 'image.png')
    image = cv2.imread(test_image_path)
    if image is None:
        return jsonify({'error': 'Test image not found. Ensure "image.png" is in the testimages directory.'}), 404
    result = extract_nid_fields(image)
    return jsonify(result)

@app.route('/testimages/<path:filename>')
def serve_image(filename):
    """Serve static files from the testimages directory."""
    return send_from_directory('testimages', filename)

if __name__ == '__main__':
    if not os.path.exists('testimages'):
        os.makedirs('testimages')
    app.run(debug=True, host='0.0.0.0')