import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clause, Sentence
from app.schemas import SentenceLabelUpdate, SentenceOut

router = APIRouter(
    prefix="/sentences",
    tags=["sentences"],
)


@router.patch("/{sentence_id}", response_model=SentenceOut)
def update_sentence_label(
    sentence_id: uuid.UUID,
    body: Annotated[SentenceLabelUpdate, Body()],
    db: Annotated[Session, Depends(get_db)],
):
    sentence = db.get(Sentence, sentence_id)
    if not sentence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sentence not found.")

    if body.clause_id is not None:
        clause = db.get(Clause, body.clause_id)
        if not clause:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clause not found.")

    sentence.label_id = body.clause_id
    db.commit()
    db.refresh(sentence)

    return SentenceOut(
        id=sentence.id,
        text=sentence.text,
        position=sentence.position,
        label_name=sentence.label.name if sentence.label else None,
        label_color=sentence.label.color if sentence.label else None,
    )
