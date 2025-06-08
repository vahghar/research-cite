# app/crud/document.py
from sqlalchemy.orm import Session
from ..models.document import DocumentStatus,Document

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
