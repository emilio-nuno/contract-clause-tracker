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

class ContractOut(BaseModel):
    id: UUID
    filename: str
    uploaded_at: datetime
    sentences: list[SentenceOut] = []