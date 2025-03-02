# Bangladesh National ID Card OCR Extractor

A robust API for extracting information from Bangladesh National ID Cards using OCR technology. This service provides a secure, rate-limited REST API that processes images and extracts key information such as name, date of birth, and ID number.

![Bangladesh NID](https://i.imgur.com/example.png)

## 📋 Features

- **Robust Text Extraction**: Uses EasyOCR with specialized patterns for Bangladesh ID cards
- **High Accuracy**: Multiple pattern matching algorithms to handle various ID card formats
- **Secure API**: Token-based authentication and request rate limiting
- **Cross-Platform**: Works on both Windows and Linux environments
- **Field Validation**: Validates extracted information against provided data
- **Resource Management**: Efficient cleaning of temporary files
- **Comprehensive Logging**: Detailed logs for debugging and auditing

## 🔧 Requirements

- Python 3.8+ (tested on Python 3.12 and 3.13)
- Flask web framework
- OpenCV for image processing
- EasyOCR for text extraction
- Storage space for model files (~100MB)

## ⚙️ Installation

### Common Setup (All Platforms)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/nid-ocr-extractor.git
   cd nid-ocr-extractor
   ```

2. **Create environment file:**

   ```bash
   # Copy example environment file
   cp .env.example .env

   # Generate secure tokens and update .env file
   python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"
   python -c "import secrets; print(f'AUTH_TOKEN={secrets.token_hex(16)}')"
   ```

### Windows Setup

1. **Create and activate virtual environment:**

   ```powershell
   python -m venv win_venv
   win_venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt

   # Windows needs python-magic-bin instead of python-magic
   pip uninstall -y python-magic
   pip install python-magic-bin
   ```

### Linux Setup

1. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install system dependencies:**

   For Debian/Ubuntu:

   ```bash
   sudo apt-get update
   sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
   ```

   For Arch Linux:

   ```bash
   sudo pacman -Syu
   sudo pacman -S mesa glib2 libx11 libxext libxrender
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Starting the Server

```bash
# Start the Flask server
python app.py
```

By default, the server runs on `http://localhost:5000`.

### Testing with the Client

The repository includes a client script for testing the API:

```bash
# Basic usage with default settings
python client.py --token YOUR_AUTH_TOKEN

# Specify a custom image
python client.py --image path/to/id/image.jpg --token YOUR_AUTH_TOKEN

# Compare with known data
python client.py --name "John Doe" --dob "15 Mar 1985" --token YOUR_AUTH_TOKEN
```

### API Endpoints

#### `GET /`

Health check endpoint that confirms the API is running.

#### `POST /process_image`

Processes an ID card image and extracts information.

**Request Headers:**

- `X-API-Token`: Your authentication token from .env file

**Form Data:**

- `image`: The image file (JPEG, PNG)
- `Name` (optional): Name for comparison
- `Date of Birth` (optional): Date of birth for comparison

**Response:**

```json
{
  "Name": "MD SAMIM MIA",
  "Date of birth": "07 Jun 1972",
  "ID Number": "9116217028",
  "Full extracted text": "...",
  "similarity": {
    "status": "no_comparison_data_provided"
  }
}
```

## ⚠️ Common Issues and Troubleshooting

### Windows Issues

1. **libmagic not found error:**

   ```
   ImportError: failed to find libmagic
   ```

   **Solution:** Replace `python-magic` with `python-magic-bin`:

   ```powershell
   pip uninstall -y python-magic
   pip install python-magic-bin
   ```

2. **DLL load failed error:**
   ```
   ImportError: DLL load failed while importing cv2
   ```
   **Solution:** Reinstall OpenCV:
   ```powershell
   pip uninstall -y opencv-python
   pip install opencv-python
   ```

### Linux Issues

1. **OpenGL/libGL.so.1 error:**

   ```
   ImportError: libGL.so.1: cannot open shared object file
   ```

   **Solution:** Install required libraries:

   ```bash
   # For Ubuntu/Debian
   sudo apt-get install -y libgl1-mesa-glx

   # For Arch Linux
   sudo pacman -S mesa
   ```

2. **Permission denied for cache directory:**
   ```
   PermissionError: [Errno 13] Permission denied: 'cache'
   ```
   **Solution:** Check permissions:
   ```bash
   chmod 750 cache
   ```

## 🛠️ Configuration

The application uses environment variables defined in .env for configuration:

| Variable           | Description                    | Default         |
| ------------------ | ------------------------------ | --------------- |
| SECRET_KEY         | Secret key for Flask           | Generated value |
| AUTH_TOKEN         | API authentication token       | Generated value |
| RATE_LIMIT         | Max requests per window        | 10              |
| RATE_LIMIT_WINDOW  | Rate limit window in seconds   | 60              |
| MAX_CONTENT_LENGTH | Max allowed file size in bytes | 5MB (5242880)   |
| CACHE_DIR          | Directory for temporary files  | cache           |

## 🔒 Security Notes

1. Always use a strong, randomly generated AUTH_TOKEN
2. The API implements rate limiting to prevent abuse
3. Temporary files are automatically deleted after processing
4. Input validation helps prevent malicious uploads
5. Security headers mitigate common web vulnerabilities

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for the OCR engine
- Flask team for the web framework
- OpenCV contributors for image processing capabilities

---

**Note:** This software is intended for legitimate identity verification purposes. Please ensure compliance with local data protection and privacy regulations when handling personal identification information.
