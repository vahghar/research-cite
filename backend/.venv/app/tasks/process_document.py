# app/tasks/process_document.py

import os
#from celery import shared_task
from sqlalchemy.orm import Session
import logging
from fastapi import UploadFile
from ..core.config import settings
from ..database import SessionLocal
from ..crud import document as crud_doc
from ..crud import summary as crud_sum
from ..crud import citation as crud_cit
from ..utils.pdf_parser import extract_text_from_pdf
from ..utils.summarizer import generate_structured_summary
from ..utils.citation_extractor import extract_reference_section, extract_citations_from_references, bibtex_to_fields

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#@shared_task(bind=True)
def process_document(self, document_id: int):
    """
    Fucntions without celery temporarily
    1. Mark document as PROCESSING
    2. Extract text (OCR if needed)
    3. Summarize into sections
    4. Extract references and parse into BibTeX
    5. Save Summary and Citation rows
    6. Mark document as COMPLETED (or FAILED on exception)
    """
    db: Session = SessionLocal()
    try:
        # 1. Fetch Document
        logger.info(f"Starting process_document for ID: {document_id}")
        db_doc = crud_doc.get_document(db, document_id)
        if not db_doc:
            return
        crud_doc.update_document_status(db, document_id, crud_doc.DocumentStatus.PROCESSING, progress=10)
        logger.info(f"Document {document_id} fetched. Status updated to PROCESSING (10%). File Path: {db_doc.file_path}")

        pdf_path = db_doc.file_path
        if not pdf_path or not os.path.exists(pdf_path):
            logger.error(f"PDF file path is invalid or does not exist for Document {document_id}: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        # 2. Extract full text (OCR if necessary)
        logger.info(f"Attempting to extract text from PDF: {pdf_path}")
        full_text = extract_text_from_pdf(pdf_path) # <--- THIS IS THE PRIMARY SUSPECT
        logger.info(f"Text extraction completed for Document {document_id}. Text length: {len(full_text)} characters.")
        crud_doc.update_document_status(db, document_id, crud_doc.DocumentStatus.PROCESSING, progress=30)
        logger.info(f"Document {document_id} status updated to PROCESSING (30%).")

        logger.info(f"Attempting to generate structured summary for Document {document_id}.")
        summary_dict = generate_structured_summary(full_text)
        logger.info(f"Summary generation completed for Document {document_id}.")
        crud_doc.update_document_status(db, document_id, crud_doc.DocumentStatus.PROCESSING, progress=60)
        logger.info(f"Document {document_id} status updated to PROCESSING (60%).")

        # 4. Save Summary in DB
        logger.info(f"Attempting to save summary for Document {document_id}.")
        crud_sum.create_summary(
            db,
            document_id=document_id,
            introduction=summary_dict.get("introduction", ""),
            methods=summary_dict.get("methods", ""),
            results=summary_dict.get("results", ""),
            conclusion=summary_dict.get("conclusion", ""),
        )
        logger.info(f"Summary saved for Document {document_id}.")

        # 5. Extract reference section & parse citations
        logger.info(f"Attempting to extract reference section for Document {document_id}.")
        ref_text = extract_reference_section(full_text)
        logger.info(f"Reference section extracted for Document {document_id}. Length: {len(ref_text)} characters.")
        bib_list = extract_citations_from_references(ref_text)
        logger.info(f"Citations extracted for Document {document_id}. Found {len(bib_list)} citations.")

        progress_step = 60
        for bibtex_str in bib_list:
            fields = bibtex_to_fields(bibtex_str)
            crud_cit.create_citation(
                db,
                document_id=document_id,
                raw_bibtex=bibtex_str,
                apa_text=fields.get("title", "") + ", " + fields.get("year", ""),
                doi=fields.get("doi", None),
                title=fields.get("title", None),
                authors=" and ".join(fields.get("author", "").split(" and ")),
                year=fields.get("year", None),
            )
            progress_step += int(20 / max(len(bib_list), 1))
            crud_doc.update_document_status(db, document_id, crud_doc.DocumentStatus.PROCESSING, progress=progress_step)
        logger.info(f"Citations saved for Document {document_id}.")


        # 6. Completed
        crud_doc.update_document_status(db, document_id, crud_doc.DocumentStatus.COMPLETED, progress=100)
        logger.info(f"Document {document_id} processing COMPLETED.")
    except Exception as e:
        logger.exception(f"FATAL ERROR during document processing for ID {document_id}. Exception: {e}") # This will print the full traceback
        crud_doc.update_document_status(db, document_id, crud_doc.DocumentStatus.FAILED)
        raise e # Re-raise to ensure the 500 error is returned by FastAPI
    finally:
        db.close()
