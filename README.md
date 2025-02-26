# NID Card OCR Extractor

Welcome to the NID Card OCR Extractor project. This tool is designed to automatically extract key information from National ID cards. It’s ideal for organizations needing fast and accurate identity verification without manual data entry.

## Features

- **Accurate Extraction**: Automatically retrieves names, birth dates, and ID numbers from NID card images.
- **Image Enhancement**: Processes and enhances low-quality images to improve OCR accuracy.
- **Simple Web Interface**: View results in real time using a user-friendly API.
- **Integrable API**: Easily integrate the extractor into your existing systems.
- **Powered by EasyOCR**: Utilizes the latest EasyOCR models for exceptional performance.

## Getting Started

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/nid-ocr-project.git
   cd nid-ocr-project
   ```

2. **Set Up Your Environment**:

   Create a virtual environment and install the dependencies:

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

   Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:

   Start the Flask server:

   ```bash
   python app.py
   ```

   Open your browser and navigate to http://localhost:5000/ to see the API running.

## Using the API

You can integrate the API into your own applications. Here is an example of how to send a request using Python:

```python
import requests

# Path to your NID card image
card_image = "path/to/nid_image.jpg"

url = "http://localhost:5000/process_image"

with open(card_image, "rb") as image_file:
    files = {"image": image_file}
    data = {
        "Name": "John Doe",
        "Date of Birth": "01 Jan 1990"
    }
    response = requests.post(url, data=data, files=files)

nid_data = response.json()
print("Extracted Information:")
print(f"Name: {nid_data['Name']}")
print(f"Date of Birth: {nid_data['Date of birth']}")
print(f"ID Number: {nid_data['ID Number']}")
```

## Customization

You can tailor the extractor to better fit your needs:

- **GPU Support**: If you have a compatible GPU, adjust the EasyOCR configuration in the code to enable GPU acceleration.
- **Preprocessing Parameters**: Modify the preprocessing settings to handle different image qualities.
- **Threshold Adjustments**: Fine-tune the detection thresholds to improve accuracy based on your specific dataset.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository. Contributions and suggestions are always welcome.

## Privacy Notice

This tool processes sensitive personal information. Make sure to use it only for legitimate purposes and comply with all applicable data protection regulations.
