# NID Card OCR Extractor

Extract information from National ID cards using advanced OCR techniques and image preprocessing.

## Features

- Extract name, date of birth, and ID number from NID cards
- Robust preprocessing for better OCR accuracy
- Web interface for visualization and testing
- API endpoint for integration with other services
- Uses EasyOCR with the advanced english_g2 model for superior recognition

## Installation

1. Clone the repository:

```

git clone https://github.com/yourusername/nid-ocr-project.git
cd nid-ocr-project

```

2. Create a virtual environment and install dependencies:

```

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

3. Run the application:

```

python app.py

```

4. Open your browser and navigate to http://localhost:5000/

## API Usage

Send a POST request to `/process_image` with an image file to extract NID information:

```python
import requests

url = "http://localhost:5000/process_image"
files = {"image": open("path/to/nid_image.jpg", "rb")}
response = requests.post(url, files=files)
nid_data = response.json()

print(nid_data)
# {'name': 'JOHN DOE', 'date_of_birth': '01 Jan 1990', 'id_number': '1234567890'}
```

## Configuration

You can modify OCR settings in app.py:

- GPU acceleration: Set `gpu=True` if you have a CUDA-compatible GPU
- OCR confidence: Adjust the threshold in the `extract_nid_fields` function
- Image preprocessing parameters can be tuned in `preprocess_for_easyocr`
