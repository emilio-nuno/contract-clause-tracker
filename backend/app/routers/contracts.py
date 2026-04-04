import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clause, Contract, Sentence
from app.schemas import ContractOut, SentenceOut
from app.services import parse_sentences

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"]
)

@router.post("/", response_model=ContractOut,status_code=status.HTTP_201_CREATED)
async def upload_contract(file: UploadFile, db: Session = Depends(get_db)) -> Contract:
    if not file.filename.lower().endswith((".txt", ".md")):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only .txt and .md files are accepted.")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("utf-8", errors="replace")

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
def get_contract(contract_id: uuid.UUID, db: Session = Depends(get_db)):
    contract = db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    return ContractOut(
        id=contract.id,
        filename=contract.filename,
        uploaded_at=contract.uploaded_at,
        sentences=[
            SentenceOut(
                id=s.id,
                text=s.text,
                position=s.position,
                label_name=s.label.name if s.label else None,
                label_color=s.label.color if s.label else None,
            )
            for s in sorted(contract.sentences, key=lambda s: s.position)
        ],
    )


@router.get("/contracts", response_model=list[ContractOut])
def get_dashboard(
    search: Optional[str] = None,
    clause_id: Optional[uuid.UUID] = None,
    group_by: Optional[str] = Query(None, pattern="^(clause|none)$"),
    db: Session = Depends(get_db),
):
    contracts = db.query(Contract)

    if search:
        contracts = contracts.filter(Contract.filename.ilike(f"%{search}%"))

    if clause_id:
        contracts = contracts.filter(
            Contract.sentences.any(Sentence.label_id == clause_id)
        )

    return [
        ContractOut(
            id=c.id,
            filename=c.filename,
            uploaded_at=c.uploaded_at,
            sentences=[],
        )
        for c in contracts.all()
    ]