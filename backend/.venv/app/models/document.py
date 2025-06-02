# app/models/document.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    source_url = Column(String, nullable=True)      # if user submitted arXiv/DOI link
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    progress = Column(Integer, default=0)            # e.g. 0..100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    summary = relationship("Summary", back_populates="document", uselist=False)
    citations = relationship("Citation", back_populates="document")
