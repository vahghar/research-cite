# app/models/citation.py
from sqlalchemy import Column, Integer, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from ..database import Base

class Citation(Base):
    __tablename__ = "citations"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # You can store whichever fields you like:
    raw_bibtex = Column(Text, nullable=False)
    apa_text = Column(Text, nullable=True)
    doi = Column(String, nullable=True, index=True)
    title = Column(String, nullable=True)
    authors = Column(String, nullable=True)
    year = Column(String, nullable=True)
    
    document = relationship("Document", back_populates="citations")
