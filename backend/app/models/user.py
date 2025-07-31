# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)   # if using password auth
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # If you store Zotero credentials per user:
    zotero_api_key = Column(String, nullable=True)
    zotero_user_id = Column(String, nullable=True)
    
    # Relationship
    documents = relationship("Document", back_populates="owner")
