from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SentenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    position: int
    label_name: Optional[str] = None
    label_color: Optional[str] = None


class ContractSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    uploaded_at: datetime


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    uploaded_at: datetime
    sentences: list[SentenceOut] = []


class ClauseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class SentenceLabelUpdate(BaseModel):
    clause_id: Optional[UUID] = None
