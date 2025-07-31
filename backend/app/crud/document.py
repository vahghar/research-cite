# app/crud/document.py
from sqlalchemy.orm import Session
from ..models.document import DocumentStatus,Document
from ..models.summary import Summary
from ..models.citation import Citation
import os

def create_document(db: Session, owner_id: int, file_path: str, original_filename: str = None, source_url: str = None):
    db_doc = Document(
        owner_id=owner_id,
        file_path=file_path,
        original_filename=original_filename,
        source_url=source_url,
        status=DocumentStatus.PENDING,
        progress=0,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents_by_owner(db: Session, owner_id: int):
    return db.query(Document).filter(Document.owner_id == owner_id).all()

def update_document_status(db: Session, document_id: int, status: DocumentStatus, progress: int = None):
    db_doc = get_document(db, document_id)
    if not db_doc:
        return None
    db_doc.status = status
    if progress is not None:
        db_doc.progress = progress
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def delete_document(db: Session, document_id: int):
    """
    Delete a document and all its related data (summary, citations, and file).
    """
    db_doc = get_document(db, document_id)
    if not db_doc:
        print(f"Document {document_id} not found")
        return False
    
    try:
        print(f"Deleting document {document_id} and related data...")
        
        # Delete related citations first
        citations = db.query(Citation).filter(Citation.document_id == document_id).all()
        print(f"Found {len(citations)} citations to delete")
        for citation in citations:
            db.delete(citation)
        
        # Delete related summary
        summary = db.query(Summary).filter(Summary.document_id == document_id).first()
        if summary:
            print(f"Deleting summary {summary.id}")
            db.delete(summary)
        else:
            print("No summary found for this document")
        
        # Delete the document
        print(f"Deleting document {document_id}")
        db.delete(db_doc)
        
        # Commit all changes
        db.commit()
        print("Database changes committed successfully")
        
        # Delete the physical file if it exists
        if db_doc.file_path and os.path.exists(db_doc.file_path):
            try:
                os.remove(db_doc.file_path)
                print(f"Physical file deleted: {db_doc.file_path}")
            except OSError as e:
                print(f"Warning: Could not delete file {db_doc.file_path}: {e}")
        else:
            print(f"Physical file not found or doesn't exist: {db_doc.file_path}")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting document {document_id}: {e}")
        return False
