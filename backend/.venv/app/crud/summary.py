# app/crud/summary.py
from sqlalchemy.orm import Session
from ..models.summary import Summary

def create_summary(db: Session, document_id: int, introduction: str, methods: str, results: str, conclusion: str):
    db_sum = Summary(
        document_id=document_id,
        introduction=introduction,
        methods=methods,
        results=results,
        conclusion=conclusion,
    )
    db.add(db_sum)
    db.commit()
    db.refresh(db_sum)
    return db_sum

def get_summary_by_document(db: Session, document_id: int):
    return db.query(Summary).filter(Summary.document_id == document_id).first()
