import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Contract, Sentence
from app.schemas import ContractOut, ContractSummaryOut
from app.services import parse_sentences

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"]
)


@router.post("/", response_model=ContractOut, status_code=status.HTTP_201_CREATED)
async def upload_contract(
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
):
    if not file.filename or not file.filename.lower().endswith((".txt", ".md")):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only .txt and .md files are accepted.")

    text = (await file.read()).decode("utf-8", errors="replace")

    if not text.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="File is empty.")

    contract = Contract(filename=file.filename, raw_text=text)
    db.add(contract)

    contract.sentences = [
        Sentence(contract_id=contract.id, text=s, position=i)
        for i, s in enumerate(parse_sentences(text))
    ]

    db.commit()
    db.refresh(contract)
    return contract


@router.get("/{contract_id}", response_model=ContractOut)
def get_contract(
    contract_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
):
    contract = (
        db.query(Contract)
        .options(selectinload(Contract.sentences).selectinload(Sentence.label))
        .filter(Contract.id == contract_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")
    return contract


@router.get("/", response_model=list[ContractSummaryOut])
def get_dashboard(
    db: Annotated[Session, Depends(get_db)],
    search: Annotated[Optional[str], Query()] = None,
    clause_id: Annotated[Optional[uuid.UUID], Query()] = None,
):
    contracts = db.query(Contract)

    if search:
        contracts = contracts.filter(Contract.filename.ilike(f"%{search}%"))

    if clause_id:
        contracts = contracts.filter(
            Contract.sentences.any(Sentence.label_id == clause_id)
        )

    return contracts.all()
