# app/schemas/citation.py
from pydantic import BaseModel
from typing import Optional

class CitationRead(BaseModel):
    id: int
    document_id: int
    raw_bibtex: str
    apa_text: Optional[str]
    doi: Optional[str]
    title: Optional[str]
    authors: Optional[str]
    year: Optional[str]

    class Config:
        orm_mode = True
