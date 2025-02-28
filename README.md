# NID Card OCR Extractor with Podman (Linux)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Windows (using Docker)](#windows-using-docker)
  - [macOS (using Docker)](#macos-using-docker)
  - [Linux with Podman](#linux-with-podman)
    - [Ubuntu/Debian](#linux-ubuntudebian)
    - [Fedora](#linux-fedora)
    - [Arch Linux](#linux-arch)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Mode with Podman](#production-mode-with-podman)
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
- **Containerized Deployment**: Includes Podman configuration for rootless, secure deployment.
- **Production-Ready**: Optimized for performance and security in production environments.

## System Requirements

- Python 3.7+
- 4GB+ RAM (8GB+ recommended for production)
- 2GB+ free disk space
- For GPU acceleration (optional): CUDA-compatible GPU with 4GB+ VRAM

## Installation

### Linux with Podman

#### Linux (Ubuntu/Debian)

1. **Update System and Install Prerequisites:**

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv git libgl1-mesa-glx libglib2.0-0
   ```

2. **Install Podman and Podman Compose:**

   ```bash
   # For Ubuntu 20.04+
   sudo apt install -y podman podman-compose

   # If podman-compose is not available, install via pip
   pip3 install podman-compose
   ```

3. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/nid-ocr-project.git
   cd nid-ocr-project
   ```

4. **Create a Virtual Environment (for development):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies (for development):**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

6. **Install Redis (for development):**
   ```bash
   sudo apt install -y redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

#### Linux (Fedora)

1. **Update System and Install Prerequisites:**

   ```bash
   sudo dnf update -y
   sudo dnf install -y python3 python3-pip git mesa-libGL glib2
   ```

2. **Install Podman (pre-installed on most Fedora systems):**

   ```bash
   sudo dnf install -y podman podman-compose

   # If podman-compose is not available
   pip3 install podman-compose
   ```

3. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/nid-ocr-project.git
   cd nid-ocr-project
   ```

4. **Create a Virtual Environment (for development):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies (for development):**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

6. **Install Redis (for development):**
   ```bash
   sudo dnf install -y redis
   sudo systemctl enable redis
   sudo systemctl start redis
   ```

#### Linux (Arch)

1. **Update System and Install Prerequisites:**

   ```bash
   sudo pacman -Syu
   sudo pacman -S python python-pip git mesa glib2
   ```

2. **Install Podman:**

   ```bash
   sudo pacman -S podman

   # Install podman-compose via pip
   pip install podman-compose
   ```

3. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/nid-ocr-project.git
   cd nid-ocr-project
   ```

4. **Create a Virtual Environment (for development):**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies (for development):**

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

6. **Install Redis (for development):**
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
   # Linux
   redis-server

   # Or using podman
   podman run -p 6379:6379 redis
   ```

2. **Start the Celery Worker**:

   ```bash
   # Activate your virtual environment first
   source venv/bin/activate

   # Run celery worker
   celery -A tasks worker --loglevel=info
   ```

3. **Run the Flask Application**:

   ```bash
   python app.py
   ```

4. **Access the API**:
   - The API will be running at `http://localhost:5000/`
   - Use the test endpoint at `http://localhost:5000/` to verify the API is working

### Production Mode with Podman

For production environments, we recommend using Podman:

1. **Create or convert the docker-compose.yml to podman-compose.yml**:

   ```yaml
   version: "3"

   services:
     api:
       build: .
       ports:
         - "5000:5000"
       volumes:
         - ./logs:/app/logs:Z
       env_file:
         - .env
       depends_on:
         - redis
       restart: always

     worker:
       build: .
       command: celery -A tasks worker --loglevel=info
       volumes:
         - ./logs:/app/logs:Z
       env_file:
         - .env
       depends_on:
         - redis
       restart: always

     redis:
       image: docker.io/redis:alpine
       ports:
         - "6379:6379"
       restart: always
   ```

   Note the `:Z` suffix on volume mounts, which is important for SELinux systems like Fedora.

2. **Build and Run the Containers**:

   ```bash
   # Using podman-compose
   podman-compose up -d --build

   # OR using podman play kube (converts docker-compose to k8s)
   podman-compose generate-k8s > nid-extractor-kube.yaml
   podman play kube nid-extractor-kube.yaml
   ```

3. **Scale Workers if Needed**:

   ```bash
   podman-compose up -d --scale worker=3
   ```

4. **Check Logs**:

   ```bash
   podman logs -f nid-checker-api_api_1
   ```

5. **Stop the Services**:

   ```bash
   podman-compose down
   ```

6. **Run as a Systemd Service** (one advantage of Podman over Docker):

   ```bash
   # Generate service files
   mkdir -p ~/.config/systemd/user
   cd ~/.config/systemd/user

   # Generate service file for API container
   podman generate systemd --name nid-checker-api_api_1 --files

   # Generate service file for worker container
   podman generate systemd --name nid-checker-api_worker_1 --files

   # Generate service file for redis container
   podman generate systemd --name nid-checker-api_redis_1 --files

   # Enable and start the services
   systemctl --user enable container-nid-checker-api_api_1.service
   systemctl --user enable container-nid-checker-api_worker_1.service
   systemctl --user enable container-nid-checker-api_redis_1.service

   systemctl --user start container-nid-checker-api_api_1.service
   systemctl --user start container-nid-checker-api_worker_1.service
   systemctl --user start container-nid-checker-api_redis_1.service
   ```

   This will make the services start automatically on boot.

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

5. **Podman Security Benefits**:
   - Rootless containers by default
   - No daemon running as root
   - Better isolation with SELinux integration on RHEL-based systems

## Performance Optimization

1. **Hardware Recommendations**:

   - For production use with high traffic: 4+ CPU cores, 8GB+ RAM
   - For GPU acceleration: NVIDIA GPU with 4GB+ VRAM

2. **Scaling Workers**:

   - Increase worker processes:
     ```bash
     podman-compose up -d --scale worker=3
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
   - Check logs with `podman logs nid-checker-api_worker_1`

3. **Memory Errors**:

   - Reduce concurrent workers
   - Increase container memory limits with `--memory` flag
   - Consider upgrading hardware for production use

4. **GPU Not Being Used**:

   - Verify CUDA installation with `nvidia-smi`
   - For Podman GPU access, ensure proper setup with:
     ```bash
     # Install nvidia-container-toolkit if needed
     podman run --device nvidia.com/gpu=all your-container
     ```

5. **Podman-Specific Issues**:
   - SELinux conflicts: Add `:z` or `:Z` suffix to volume mounts
   - Network connectivity: Use `--network=host` for simpler networking

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
