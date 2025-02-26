# 📝 NID Card OCR Extractor

Hey there! Welcome to the NID Card OCR project - a smart tool that helps you extract information from National ID cards without the hassle of manual data entry. Perfect for businesses, government offices, or anyone dealing with identity verification!

## ✨ What Can It Do?

- 🔍 **Smart Extraction**: Automatically pulls out names, birth dates, and ID numbers from NID cards
- 🖼️ **Image Enhancement**: Makes even low-quality card photos readable with advanced preprocessing
- 🌐 **User-Friendly Interface**: Check out the results in real-time through our simple web interface
- 🔌 **Ready-to-Use API**: Easily integrate with your existing systems and applications
- 🚀 **Powered by EasyOCR**: Uses the cutting-edge english_g2 model for exceptional accuracy

## 🚀 Getting Started

### Installation

First time using this tool? No worries! Follow these simple steps:

1. **Get the code**:

   ```bash
   git clone https://github.com/yourusername/nid-ocr-project.git
   cd nid-ocr-project
   ```

2. **Set up your environment**:

   ```bash
   # Create a cozy virtual environment for our dependencies
   python -m venv venv

   # Activate it (choose the right command for your system)
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install all the necessary packages
   pip install -r requirements.txt
   ```

3. **Let's run it!**:

   ```bash
   python app.py
   ```

4. That's it! Now open your browser and go to http://localhost:5000/

## 🔌 Using the API

Want to integrate this with your own application? It's super straightforward!

```python
import requests

# Your NID card image - replace with your actual image path
card_image = "path/to/nid_image.jpg"

# Send it to the API
url = "http://localhost:5000/process_image"
files = {"image": open(card_image, "rb")}
response = requests.post(url, files=files)

# Get the extracted details
nid_data = response.json()
print("✅ Extracted information:")
print(f"👤 Name: {nid_data['name']}")
print(f"🎂 Date of Birth: {nid_data['date_of_birth']}")
print(f"🆔 ID Number: {nid_data['id_number']}")
```

## ⚙️ Customization

Want to tweak things to fit your needs? Here's how:

- **Got a GPU?** Change `gpu=False` to `gpu=True` in app.py for lightning-fast processing!
- **Need better accuracy?** Try adjusting the confidence threshold (currently set to 0.2)
- **Have special images?** Play with the preprocessing parameters to get the best results

## 🤔 Need Help?

Feel free to open an issue if you run into problems or have questions. We're here to help make your ID processing smoother and faster!

## 🔒 Privacy First

Remember that ID cards contain sensitive information. This tool is designed for legitimate use cases with proper consent. Always ensure you're complying with local privacy laws when processing identification documents.
