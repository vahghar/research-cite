# app/schemas/summary.py
from pydantic import BaseModel

class SummaryRead(BaseModel):
    id: int
    document_id: int
    introduction: str
    methods: str
    results: str
    conclusion: str
    eli5_summary: str | None = None

    class Config:
        orm_mode = True
