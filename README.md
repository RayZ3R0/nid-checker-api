# NID Card OCR Extractor

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
  - [Linux (Fedora)](#linux-fedora)
  - [Linux (Arch)](#linux-arch)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [API Documentation](#api-documentation)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Privacy and Compliance](#privacy-and-compliance)

## Introduction

The NID Card OCR Extractor is designed to automatically extract key information from National ID cards using advanced optical character recognition. The system processes ID card images and extracts personal information including name, date of birth, and ID number. It can also compare extracted data with provided information, offering a similarity score for verification purposes.

This tool is ideal for organizations requiring fast and accurate identity verification without manual data entry, such as financial institutions, government agencies, and businesses with strict KYC (Know Your Customer) requirements.

## Features

- **Accurate Information Extraction**: Automatically extracts names, birth dates, and ID numbers from NID card images with high precision.
- **Image Enhancement**: Processes and enhances low-quality images to improve OCR accuracy.
- **Data Verification**: Compares extracted information with provided data and returns similarity scores.
- **Scalable Architecture**: Uses Celery and Redis for background processing to handle high load scenarios.
- **Secure API**: Implements authentication and secure file handling.
- **Containerized Deployment**: Includes Docker configuration for easy deployment.
- **Production-Ready**: Optimized for performance and security in production environments.

## System Requirements

- Python 3.7+
- 4GB+ RAM (8GB+ recommended for production)
- 2GB+ free disk space
- For GPU acceleration (optional): CUDA-compatible GPU with 4GB+ VRAM

## Installation

### Windows

1. **Install Python:**

   - Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/windows/)
   - During installation, check "Add Python to PATH"

2. **Install Git:**

   - Download and install from [git-scm.com](https://git-scm.com/download/win)

3. **Clone the Repository:**

   ```powershell
   git clone https://github.com/RayZ3R0/nid-checker-api.git
   cd nid-checker-api
   ```

4. **Create a Virtual Environment:**

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install Dependencies:**

   ```powershell
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

6. **Environment Setup:**
   - Create a .env file in the project root using the provided template
   - For Windows, use Docker Desktop to run Redis if needed

### macOS

1. **Install Homebrew:**

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and Git:**

   ```bash
   brew install python git
   ```

3. **Clone the Repository:**

   ```bash
   git clone https://github.com/RayZ3R0/nid-checker-api.git
   cd nid-checker-api
   ```

4. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

6. **Environment Setup:**
   - Create a .env file in the project root
   - Install Redis if needed: `brew install redis`

### Linux (Ubuntu/Debian)

1. **Update System and Install Prerequisites:**

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv git libgl1-mesa-glx libglib2.0-0
   ```

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/RayZ3R0/nid-checker-api.git
   cd nid-checker-api
   ```

3. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

5. **Install Redis:**
   ```bash
   sudo apt install -y redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

### Linux (Fedora)

1. **Update System and Install Prerequisites:**

   ```bash
   sudo dnf update -y
   sudo dnf install -y python3 python3-pip git mesa-libGL glib2
   ```

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/RayZ3R0/nid-checker-api.git
   cd nid-checker-api
   ```

3. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

5. **Install Redis:**
   ```bash
   sudo dnf install -y redis
   sudo systemctl enable redis
   sudo systemctl start redis
   ```

### Linux (Arch)

1. **Update System and Install Prerequisites:**

   ```bash
   sudo pacman -Syu
   sudo pacman -S python python-pip git mesa glib2
   ```

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/RayZ3R0/nid-checker-api.git
   cd nid-checker-api
   ```

3. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

5. **Install Redis:**
   ```bash
   sudo pacman -S redis
   sudo systemctl enable redis
   sudo systemctl start redis
   ```

## Configuration

1. **Create a .env file in the project root directory:**

   ```
   # API Authentication
   API_USERNAME=admin
   API_PASSWORD=change_this_password_in_production

   # OCR Parameters
   MAX_CONTENT_LENGTH=5242880
   CACHE_DIR=cache
   OCR_BEAM_WIDTH=5
   OCR_CONTRAST_THS=0.1
   OCR_ADJUST_CONTRAST=0.5
   OCR_TEXT_THRESHOLD=0.7
   OCR_LOW_TEXT=0.4
   OCR_LINK_THRESHOLD=0.4

   # Redis configuration
   REDIS_URL=redis://localhost:6379/0
   ```

2. **Warning**: Never commit the .env file to version control as it contains sensitive information.

3. **Optional GPU Configuration**:
   - If you have a CUDA-compatible GPU, the system will automatically detect and use it.
   - Ensure you have installed the appropriate CUDA toolkit and drivers for your system.

## Running the Application

### Development Mode

1. **Start Redis** (if not already running):

   ```bash
   # Linux/macOS
   redis-server

   # Windows (using Docker)
   docker run -p 6379:6379 redis
   ```

2. **Start the Celery Worker**:

   ```bash
   # Activate your virtual environment first
   celery -A tasks worker --loglevel=info
   ```

3. **Run the Flask Application**:

   ```bash
   python app.py
   ```

4. **Access the API**:
   - The API will be running at `http://localhost:5000/`
   - Use the test endpoint at `http://localhost:5000/` to verify the API is working

### Production Mode

For production environments, we strongly recommend using Docker:

1. **Make sure Docker and Docker Compose are installed**:

   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
   - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

2. **Build and Run the Docker Containers**:

   ```bash
   docker-compose up -d --build
   ```

3. **Scale Workers if Needed**:

   ```bash
   docker-compose up -d --scale worker=3
   ```

4. **Check Logs**:

   ```bash
   docker-compose logs -f api
   ```

5. **Stop the Services**:
   ```bash
   docker-compose down
   ```

## API Documentation

### Authentication

All API endpoints require HTTP Basic Authentication:

- Username: Set in .env as `API_USERNAME`
- Password: Set in .env as `API_PASSWORD`

### Endpoints

#### 1. Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Description**: Test if the API is running.
- **Response**: `{"message": "NID Extractor API is running."}`

#### 2. Process Image

- **URL**: `/process_image`
- **Method**: `POST`
- **Description**: Process an NID card image and extract information.

- **Request parameters**:

  - `image`: The image file (required)
  - `Name`: Optional name for comparison
  - `Date of Birth`: Optional DOB for comparison

- **Response format**:
  ```json
  {
    "Name": "John Doe",
    "Date of birth": "01 Jan 1990",
    "ID Number": "1234567890",
    "Full extracted text": "...",
    "similarity": {
      "status": "partial_comparison",
      "name_similarity": 0.85,
      "dob_similarity": 0.92
    }
  }
  ```
- **For long-running tasks** (response if processing exceeds timeout):
  ```json
  {
    "status": "processing",
    "task_id": "task-uuid-here",
    "message": "Image processing is taking longer than expected. Check back using the task_id."
  }
  ```

#### 3. Check Task Status

- **URL**: `/check_task/<task_id>`
- **Method**: `GET`
- **Description**: Check status of a task that exceeded the timeout.
- **Response**: Same as process_image when complete, or status update if still processing.

#### 4. Check Task with Comparison Data

- **URL**: `/check_task_with_comparison/<task_id>`
- **Method**: `POST`
- **Description**: Check task status and add comparison data.
- **Request parameters**:
  - `Name`: Name for comparison
  - `Date of Birth`: DOB for comparison

## Security Considerations

1. **API Authentication**:

   - Change default credentials in production
   - Consider using stronger authentication methods for sensitive deployments

2. **File Uploads**:

   - The API validates file types and sizes
   - Temporary files are automatically cleaned up after processing

3. **Private Data**:

   - NID cards contain sensitive personal information
   - Ensure your application complies with data protection regulations
   - Do not store extracted data unless necessary and legal

4. **Network Security**:
   - For production, place the API behind a reverse proxy like Nginx
   - Configure HTTPS to encrypt data in transit

## Performance Optimization

1. **Hardware Recommendations**:

   - For production use with high traffic: 4+ CPU cores, 8GB+ RAM
   - For GPU acceleration: NVIDIA GPU with 4GB+ VRAM

2. **Scaling Workers**:

   - Increase worker processes in docker-compose.yml:
     ```yaml
     docker-compose up -d --scale worker=3
     ```

3. **Redis Configuration**:
   - For high load, consider tuning Redis or moving to a dedicated instance

## Troubleshooting

### Common Issues

1. **OCR Quality Problems**:

   - Ensure images are clear and well-lit
   - Try adjusting OCR parameters in .env
   - For complex layouts, use preprocessing or consider training a custom model

2. **Workers Not Processing**:

   - Check Redis connection
   - Verify Celery workers are running
   - Check logs with `docker-compose logs worker`

3. **Memory Errors**:

   - Reduce concurrent workers
   - Increase container memory limits
   - Consider upgrading hardware for production use

4. **GPU Not Being Used**:
   - Verify CUDA installation with `nvidia-smi`
   - Check that PyTorch can access GPU with:
     ```python
     import torch; print(torch.cuda.is_available())
     ```

## Privacy and Compliance

This tool processes sensitive personal information from ID documents. Users must ensure:

1. **Legal Basis**: Have a legal basis for processing ID documents
2. **Consent**: Obtain proper consent where required
3. **Data Minimization**: Only collect and store necessary data
4. **Security**: Implement appropriate security measures
5. **Compliance**: Adhere to relevant regulations such as GDPR, CCPA, etc.

**Warning**: Misuse of this tool for identity theft or fraud is illegal. Users are responsible for ensuring their use of the NID Extractor complies with all applicable laws and regulations.

---

For additional support or contributions, please open an issue in the GitHub repository.
