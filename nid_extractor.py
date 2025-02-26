import itertools
import difflib
import re
import cv2
import easyocr
import spacy
import logging
from config import OCR_PARAMS

logger = logging.getLogger(__name__)

# Load the spaCy English model.
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Loaded spaCy model: en_core_web_sm")
except Exception:
    logger.exception("Failed to load spaCy model.")

# Initialize EasyOCR – if no GPU is available, fall back to CPU.
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
    logger.info("Initialized EasyOCR using GPU" if gpu_available else "Initialized EasyOCR using CPU")
except Exception:
    logger.exception("Error initializing EasyOCR with GPU; falling back to CPU")
    reader = easyocr.Reader(
        ['en'],
        gpu=False,
        model_storage_directory='model',
        download_enabled=True,
        recog_network='english_g2'
    )

def clean_name(name: str) -> str:
    """Remove common prefixes and normalize the name."""
    try:
        name = re.sub(r'^(?:nama|name)[:\s]+', '', name, flags=re.IGNORECASE)
        return ' '.join(name.split())
    except Exception:
        logger.exception("Error cleaning name.")
        return name

def extract_front_name(cleaned_text: str) -> str:
    """
    Extract the front side name using patterns.
    Try strict patterns first, then looser ones.
    """
    patterns = [
        r"(?:Nama|Name)[:\s]+((?:[A-Z][a-zA-Z\.\']+\s+){1,5}[A-Z][a-zA-Z\.\']+)",
        r"(?:Nama|Name)\s+([A-Z][a-zA-Z\s]+)"
    ]
    for pattern in patterns:
        try:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except Exception:
            logger.exception("Error matching front name pattern.")
    return ""

def extract_mrz_name(mrz_text: str):
    """
    Extract name components from MRZ text.
    Looks for the last line with many '<' characters,
    splits on '<<' and '<', cleans each part and filters noise.
    """
    try:
        lines = mrz_text.split('\n')
    except Exception:
        logger.exception("Error splitting MRZ text.")
        return None

    mrz_line = None
    for line in reversed(lines):
        if line.count('<') > 5:
            mrz_line = line.upper()
            break
    if not mrz_line:
        return None

    segments = mrz_line.split('<<')
    name_parts = []
    for segment in segments:
        try:
            parts = [p.strip() for p in segment.split('<') if p.strip()]
        except Exception:
            logger.exception("Error splitting segment.")
            continue
        for part in parts:
            try:
                cleaned = re.sub(r'[0-9BGD]', '', part)
                cleaned = re.sub(r'[^A-Z]', '', cleaned)
                if cleaned and len(cleaned) >= 2:
                    if cleaned in ['MD', 'KD']:
                        cleaned = 'MD'
                    name_parts.append(cleaned)
            except Exception:
                logger.exception("Error cleaning MRZ part.")
                continue

    filtered_parts = []
    seen = set()
    for part in name_parts:
        if part not in seen and len(part) > 1 and not any(noise in part for noise in ['TTT', 'III']):
            filtered_parts.append(part)
            seen.add(part)
    return filtered_parts if filtered_parts else None

def find_best_name_arrangement(front_name: str, mrz_parts) -> (str, float):
    """
    Try all permutations of MRZ parts and score them against the front name.
    Return the candidate if sufficient similarity exists.
    """
    if not mrz_parts:
        return None, 0

    front_clean = clean_name(front_name).upper()
    front_words = front_clean.split()
    best_score = 0
    best_arrangement = None

    for perm in itertools.permutations(mrz_parts):
        try:
            candidate = ' '.join(p.upper() for p in perm)
            candidate_words = candidate.split()
            base_score = difflib.SequenceMatcher(None, front_clean, candidate).ratio()
            word_matches = 0
            partial_matches = 0

            for w1 in front_words:
                best_match = 0
                for w2 in candidate_words:
                    similarity = difflib.SequenceMatcher(None, w1, w2).ratio()
                    if similarity > best_match:
                        best_match = similarity
                if best_match > 0.9:
                    word_matches += 1
                elif best_match > 0.7:
                    partial_matches += 0.5

            word_score = (word_matches + partial_matches) / len(front_words)
            len_ratio = min(len(candidate), len(front_clean)) / max(len(candidate), len(front_clean))
            total_score = (base_score * 0.3 + word_score * 0.5 + len_ratio * 0.2)

            if total_score > best_score:
                best_score = total_score
                best_arrangement = candidate
        except Exception:
            logger.exception("Error evaluating candidate arrangement.")
            continue

    return best_arrangement, best_score

def extract_nid_fields(image) -> dict:
    """
    Extract and validate NID fields from the given image using OCR.
    Returns a dictionary with the extracted information.
    
    NOTE: For higher loads, consider offloading this function asynchronously,
    e.g. by using Celery.
    """
    nid_data = {
        'Name': '',
        'Date of birth': '',
        'ID Number': '',
        'Full extracted text': ''
    }

    try:
        results = reader.readtext(
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
    except Exception:
        logger.exception("OCR processing failed.")
        nid_data['error'] = "OCR processing failed."
        return nid_data

    text_blocks = []
    for result in results:
        try:
            if len(result) >= 2:
                text_blocks.append(result[1])
        except Exception:
            logger.exception("Error processing an OCR result.")
            continue

    full_text = "\n".join(text_blocks)
    nid_data['Full extracted text'] = full_text

    # Clean text
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', full_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Extract Name parts
    front_name = extract_front_name(cleaned_text)
    mrz_parts = extract_mrz_name(cleaned_text)

    if front_name and mrz_parts:
        arranged_name, similarity = find_best_name_arrangement(front_name, mrz_parts)
        logger.info(f"Front name: {front_name}, MRZ parts: {mrz_parts}, Arranged: {arranged_name} (score: {similarity})")
        front_parts = set(w.upper() for w in front_name.split())
        arranged_parts = set(w.upper() for w in arranged_name.split()) if arranged_name else set()
        common_parts = front_parts.intersection(arranged_parts)
        if arranged_name and similarity >= 0.3 and len(common_parts) >= min(2, len(front_parts)):
            final_name = arranged_name
        else:
            final_name = clean_name(front_name)
    elif front_name:
        final_name = clean_name(front_name)
    else:
        final_name = "Error: No valid name found"
    nid_data['Name'] = final_name

    # Extract Date of Birth.
    dob_patterns = [
        r"(?:Date of Birth|DOB|Birth)[:\s]+(\d{1,2}[\s-]*[A-Za-z]+[\s-]*\d{4})",
        r"(?:Date of Birth|DOB|Birth)[:\s]+(\d{1,2}[\s/-]*\d{1,2}[\s/-]*\d{2,4})",
        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
    ]
    for pattern in dob_patterns:
        try:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                nid_data['Date of birth'] = match.group(1).strip()
                break
        except Exception:
            logger.exception("Error matching DOB pattern.")
            continue

    # Extract ID Number.
    try:
        id_match = re.search(r'\bNID\s*No\.?\s*((?:\d[\s]*){10,})', cleaned_text, re.IGNORECASE)
        if id_match:
            num = re.sub(r'\s+', '', id_match.group(1))
            nid_data['ID Number'] = num[:10]
        else:
            id_match = re.search(r'\b\d{10,}\b', cleaned_text)
            if id_match:
                nid_data['ID Number'] = id_match.group(0)
    except Exception:
        logger.exception("Error extracting ID Number.")

    return nid_data