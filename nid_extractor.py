import easyocr
import logging
import os
import re
import cv2
import numpy as np
from config import OCR_PARAMS

# Configure logging for this module
logger = logging.getLogger(__name__)

# Lazy-loaded reader instance to avoid multiple initializations
reader = None

def get_reader():
    """Lazy load the OCR reader to avoid multiple initializations"""
    global reader
    if reader is None:
        try:
            import torch
            gpu_available = torch.cuda.is_available()
            reader = easyocr.Reader(
                ['en'],
                gpu=gpu_available,
                model_storage_directory='model',
                download_enabled=True,
                recog_network='english_g2'
            )
            logger.info(f"Initialized EasyOCR using {'GPU' if gpu_available else 'CPU'}")
        except Exception:
            logger.exception("Error initializing EasyOCR with GPU; falling back to CPU")
            reader = easyocr.Reader(
                ['en'],
                gpu=False,
                model_storage_directory='model',
                download_enabled=True,
                recog_network='english_g2'
            )
    return reader

def extract_nid_fields(image) -> dict:
    """
    Extract and validate NID fields from the given image using OCR.
    Returns a dictionary with the extracted information.
    """
    nid_data = {
        'Name': '',
        'Date of birth': '',
        'ID Number': '',
        'Full extracted text': ''
    }

    try:
        # Handle different image input formats
        if isinstance(image, str):
            # If image is a file path
            if not os.path.exists(image):
                logger.error(f"Image file not found: {image}")
                nid_data['error'] = "Image file not found"
                return nid_data
            logger.info(f"Processing image from path: {image}")
        elif isinstance(image, np.ndarray):
            # If image is already a numpy array
            logger.info("Processing image from numpy array")
        else:
            logger.error(f"Unsupported image format: {type(image)}")
            nid_data['error'] = "Unsupported image format"
            return nid_data

        # Get the reader instance lazily
        ocr_reader = get_reader()
        logger.info("Starting OCR reading...")
        
        try:
            results = ocr_reader.readtext(
                image,
                paragraph=True,
                detail=1,
                decoder='greedy',
                beamWidth=OCR_PARAMS.get("beamWidth", 5),
                contrast_ths=OCR_PARAMS.get("contrast_ths", 0.1),
                adjust_contrast=OCR_PARAMS.get("adjust_contrast", 0.5),
                text_threshold=OCR_PARAMS.get("text_threshold", 0.7),
                low_text=OCR_PARAMS.get("low_text", 0.4),
                link_threshold=OCR_PARAMS.get("link_threshold", 0.4),
            )
            logger.info(f"OCR reading completed, found {len(results)} text blocks")
        except Exception as e:
            logger.exception(f"Error during OCR reading: {e}")
            nid_data['error'] = f"OCR reading failed: {str(e)}"
            return nid_data
        
        # Process the results to extract text
        if not results:
            logger.warning("No text detected in the image")
            nid_data['error'] = "No text detected in the image"
            return nid_data
        
        # Extract full text from OCR results
        full_text = ""
        for detection in results:
            full_text += detection[1] + " "
        
        nid_data['Full extracted text'] = full_text.strip()
        
        # Extract name (assuming first line contains name)
        name_pattern = r'(?:Name|NAME)[:]*\s*([A-Za-z\s]+)'
        name_match = re.search(name_pattern, full_text)
        if name_match:
            nid_data['Name'] = name_match.group(1).strip()
        
        # Extract date of birth
        dob_pattern = r'(?:Date of Birth|DOB)[:]*\s*(\d{1,2}[\s-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s-]\d{2,4})'
        dob_match = re.search(dob_pattern, full_text, re.IGNORECASE)
        if dob_match:
            nid_data['Date of birth'] = dob_match.group(1).strip()
        
        # Extract ID number
        id_pattern = r'(?:ID|ID Number|No)[:]*\s*(\d{6,15})'
        id_match = re.search(id_pattern, full_text, re.IGNORECASE)
        if id_match:
            nid_data['ID Number'] = id_match.group(1).strip()
        
        logger.info(f"Extraction completed: {nid_data}")
        return nid_data
        
    except Exception as e:
        logger.exception(f"OCR processing failed: {str(e)}")
        nid_data['error'] = f"OCR processing failed: {str(e)}"
        return nid_data