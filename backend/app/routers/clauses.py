from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clause
from app.schemas import ClauseOut

router = APIRouter(
    prefix="/clauses",
    tags=["clauses"],
)


@router.get("/", response_model=list[ClauseOut])
def get_clauses(db: Annotated[Session, Depends(get_db)]):
    return [
        ClauseOut(
            id=c.id,
            name=c.name,
            description=c.description,
            color=c.color,
        )
        for c in db.query(Clause).all()
    ]
