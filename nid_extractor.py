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
        text_blocks = []
        for result in results:
            try:
                if len(result) >= 2:  # As long as we have bbox and text
                    text = result[1]
                    text_blocks.append(text)
            except Exception as e:
                logger.exception(f"Error processing OCR result block: {e}")
                continue
        
        full_text = " ".join(text_blocks)
        nid_data['Full extracted text'] = full_text.strip()
        
        # IMPROVED NAME PATTERNS
        name_patterns = [
            # Match "Name:" label followed by name until common boundaries
            r'Name[:.]?\s+([A-Za-z\s\.]+?)(?=\s+(?:fet|ent|Date|Birth|DOB|NID|ID|No|\d)|\n|$)',
            
            # Match "Name:" label with Bengali characters possibly in between
            r'Name[:.]?(?:[^\n:]{0,20})?([A-Za-z][A-Za-z\.\s]{3,30})(?=\s+(?:fet|ent|Date|Birth|DOB|NID|ID|No|\d)|\n|$)',
            
            # Common Bangladesh name format with "MD" or "Md." prefix
            r'\b(?:MD|Md)\.?\s+([A-Za-z]+\s+[A-Za-z]+(?:\s+[A-Za-z]+)?)\b',
            
            # Common name patterns
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        ]
        
        # Blacklist of phrases that should never be considered names
        name_blacklist = [
            "NATIONAL ID CARD", "ID CARD", "BANGLADESH", "GOVERNMENT", 
            "PEOPLES", "REPUBLIC", "CARD", "NATIONAL", "DATE OF BIRTH"
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, full_text, re.IGNORECASE)
            if name_match:
                name_candidate = name_match.group(1).strip()
                
                # Skip if name is in blacklist
                if any(blacklisted.lower() in name_candidate.lower() for blacklisted in name_blacklist):
                    logger.info(f"Skipping blacklisted name: {name_candidate}")
                    continue
                    
                # Validate name has reasonable length and format
                if ' ' in name_candidate and 4 <= len(name_candidate) <= 40:
                    nid_data['Name'] = name_candidate
                    logger.info(f"Found valid name: {name_candidate}")
                    break
                elif len(name_candidate) > 5 and not re.search(r'\d', name_candidate):
                    nid_data['Name'] = name_candidate
                    logger.info(f"Found potential single-word name: {name_candidate}")
                    # Don't break, keep looking for better matches
        
        # Extract date of birth with multiple patterns
        dob_patterns = [
            r'(?:Date of Birth|DOB|Birth)[:.]?\s*(\d{1,2}[\s-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s-]\d{2,4})',
            r'(?:Date of Birth|DOB|Birth)[:.]?\s*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'(\d{1,2}[\s-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s-]\d{2,4})'
        ]
        
        for pattern in dob_patterns:
            dob_match = re.search(pattern, full_text, re.IGNORECASE)
            if dob_match:
                nid_data['Date of birth'] = dob_match.group(1).strip()
                logger.info(f"Found date of birth: {dob_match.group(1).strip()}")
                break
        
        # COMPREHENSIVE ID NUMBER PATTERNS
        id_patterns = [
            # Match "ID NO:" format 
            r'ID\s*NO[:.]?\s*(\d[\d\s-]{5,18}\d)',
            
            # Match "NID No" format
            r'NID\s*No[:.]?\s*(\d[\d\s-]{5,18}\d)',
            
            # Match exact Bangladesh NID format with spaces
            r'\b(\d{3}\s+\d{3}\s+\d{4})\b',
            
            # Match exact Bangladesh NID format with no spaces
            r'\b(\d{10}|\d{13}|\d{17})\b',
            
            # Match NID in machine-readable zone format
            r'[<I]BGD(\d{9,})[<\d]',
            
            # Match any format with explicit ID label
            r'(?:ID|NID|Number|No)[:.]\s*(\d[\d\s-]+\d)',
            
            # Match numbers with spaces or dashes
            r'\b(\d{3}[\s-]?\d{3}[\s-]?\d{4})\b',
            
            # Last resort - match any 10+ digit sequence
            r'\b(\d{10,})\b'
        ]
        
        for pattern in id_patterns:
            id_match = re.search(pattern, full_text)
            if id_match:
                id_text = id_match.group(1)
                # Clean up spaces and dashes in the ID number
                clean_id = re.sub(r'[\s-]', '', id_text)
                
                # Validate: Bangladesh NIDs are typically 10, 13, or 17 digits
                if len(clean_id) in [10, 13, 17]:
                    nid_data['ID Number'] = clean_id
                    logger.info(f"Found valid ID number format: {clean_id} (length: {len(clean_id)})")
                    break
                else:
                    # Even if length is unusual, keep it if it looks like an ID
                    nid_data['ID Number'] = clean_id
                    logger.info(f"Found ID with unusual length: {clean_id} (length: {len(clean_id)})")
                    # Continue searching for better matches
        
        logger.info(f"Extraction completed: {nid_data}")
        return nid_data
        
    except Exception as e:
        logger.exception(f"OCR processing failed: {str(e)}")
        nid_data['error'] = f"OCR processing failed: {str(e)}"
        return nid_data