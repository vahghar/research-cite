# app/utils/pdf_parser.py

import os
import fitz
from .ocr import run_ocr_if_needed

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Attempts to extract text directly via PyMuPDF. If the text is empty on a page,
    we assume it’s a scanned page and run OCR.
    """
    text_chunks = []
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        if page_text.strip() == "":
            # Scanned page – run OCR
            ocr_text = run_ocr_if_needed(pdf_path, page_num)
            text_chunks.append(ocr_text)
        else:
            text_chunks.append(page_text)
    full_text = "\n".join(text_chunks)
    return full_text

def split_text_into_chunks(full_text: str, max_chars: int = 4000) -> list[str]:
    """
    Naïvely split by paragraphs until ~max_chars, so each chunk stays
    under LLM’s context window. You can also split by sentences.
    """
    paragraphs = full_text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += para + "\n\n"
        else:
            chunks.append(current.strip())
            current = para + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks
