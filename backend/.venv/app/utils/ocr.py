# app/utils/ocr.py

import tempfile
from pdf2image import convert_from_path
import pytesseract

def run_ocr_if_needed(pdf_path: str, page_num: int) -> str:
    """
    Given a PDF path and a page number, convert that page to image
    and run pytesseract OCR, returning extracted text.
    """
    # Convert only the specified page to an image
    images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1, dpi=300)
    if not images:
        return ""
    img = images[0]
    text = pytesseract.image_to_string(img)
    return text
