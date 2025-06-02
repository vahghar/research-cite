# app/schemas/document.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentCreate(BaseModel):
    # Either file upload or a URL; we handle file upload separately in route
    source_url: Optional[str] = None

class DocumentRead(BaseModel):
    id: int
    owner_id: int
    original_filename: Optional[str]
    source_url: Optional[str]
    status: DocumentStatus
    progress: int

    class Config:
        orm_mode = True

class DocumentStatusResponse(BaseModel):
    id: int
    status: DocumentStatus
    progress: int

    class Config:
        orm_mode = True
