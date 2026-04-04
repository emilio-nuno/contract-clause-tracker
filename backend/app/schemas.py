"""
Return Models
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from datetime import datetime

class SentenceOut(BaseModel):
    id: UUID
    text: str
    position: int
    label_name: Optional[str] = None
    label_color: Optional[str] = None

class ContractSummaryOut(BaseModel):
    id: UUID
    filename: str
    uploaded_at: datetime

class ContractOut(BaseModel):
    id: UUID
    filename: str
    uploaded_at: datetime
    sentences: list[SentenceOut] = []


class ClauseOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class SentenceLabelUpdate(BaseModel):
    clause_id: Optional[UUID] = None