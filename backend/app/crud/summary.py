# app/crud/summary.py
from sqlalchemy.orm import Session
from ..models.summary import Summary

def create_summary(db: Session, document_id: int, introduction: str, methods: str, results: str, conclusion: str, eli5_summary: str = None):
    db_sum = Summary(
        document_id=document_id,
        introduction=introduction,
        methods=methods,
        results=results,
        conclusion=conclusion,
        eli5_summary=eli5_summary,
    )
    db.add(db_sum)
    db.commit()
    db.refresh(db_sum)
    return db_sum

def get_summary_by_document(db: Session, document_id: int):
    return db.query(Summary).filter(Summary.document_id == document_id).first()

def update_eli5_summary(db: Session, document_id: int, eli5_summary: str):
    summary = db.query(Summary).filter(Summary.document_id == document_id).first()
    if summary:
        summary.eli5_summary = eli5_summary
        db.commit()
        db.refresh(summary)
    return summary

def delete_summary(db: Session, summary_id: int):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if summary:
        db.delete(summary)
        db.commit()

