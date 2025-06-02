# app/crud/citation.py
from sqlalchemy.orm import Session
from ..models.citation import Citation

def create_citation(db: Session, document_id: int, raw_bibtex: str, apa_text: str = None, doi: str = None, title: str = None, authors: str = None, year: str = None):
    db_cit = Citation(
        document_id=document_id,
        raw_bibtex=raw_bibtex,
        apa_text=apa_text,
        doi=doi,
        title=title,
        authors=authors,
        year=year,
    )
    db.add(db_cit)
    db.commit()
    db.refresh(db_cit)
    return db_cit

def get_citations_by_document(db: Session, document_id: int):
    return db.query(Citation).filter(Citation.document_id == document_id).all()
