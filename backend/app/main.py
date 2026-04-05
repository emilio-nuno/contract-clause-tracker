from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, engine
from app.models import Base, Clause, Contract, Sentence
from app.routers.clauses import router as clauses_router
from app.routers.contracts import router as contracts_router
from app.routers.sentences import router as sentences_router

SEED_CLAUSES = [
    Clause(name="Limitation of Liability", description="Caps the damages one party can claim from the other.", color="#ef4444"),
    Clause(name="Termination for Convenience", description="Allows a party to end the contract without cause.", color="#f97316"),
    Clause(name="Non-Compete", description="Restricts a party from competing during or after the contract.", color="#eab308"),
    Clause(name="Confidentiality", description="Obligates parties to keep certain information secret.", color="#3b82f6"),
    Clause(name="Indemnification", description="Requires one party to compensate the other for specified losses.", color="#8b5cf6"),
    Clause(name="Force Majeure", description="Excuses performance obligations due to extraordinary events.", color="#06b6d4"),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add_all(SEED_CLAUSES)
        db.flush()

        limitation_clause = SEED_CLAUSES[0]
        confidentiality_clause = SEED_CLAUSES[3]

        contract1 = Contract(
            filename="contract1.md",
            raw_text="The liability of either party shall not exceed the total fees paid under this agreement.",
        )
        sentence1_1 = Sentence(
            text="The liability of either party shall not exceed the total fees paid under this agreement.",
            position=0,
            contract=contract1,
            label=limitation_clause,
        )

        contract2 = Contract(
            filename="contract2.txt",
            raw_text="This agreement shall commence on the date of signing. Either party may terminate this agreement with thirty days written notice.",
        )
        sentence2_1 = Sentence(
            text="This agreement shall commence on the date of signing.",
            position=0,
            contract=contract2,
        )
        sentence2_2 = Sentence(
            text="Either party may terminate this agreement with thirty days written notice.",
            position=1,
            contract=contract2,
        )

        contract3 = Contract(
            filename="contract3.md",
            raw_text="All information shared under this contract is strictly confidential. The receiving party agrees not to disclose any proprietary data. Disputes shall be resolved through binding arbitration.",
        )
        sentence3_1 = Sentence(
            text="All information shared under this contract is strictly confidential.",
            position=0,
            contract=contract3,
            label=confidentiality_clause,
        )
        sentence3_2 = Sentence(
            text="The receiving party agrees not to disclose any proprietary data.",
            position=1,
            contract=contract3,
            label=confidentiality_clause,
        )
        sentence3_3 = Sentence(
            text="Disputes shall be resolved through binding arbitration.",
            position=2,
            contract=contract3,
        )

        db.add_all([
            contract1, sentence1_1,
            contract2, sentence2_1, sentence2_2,
            contract3, sentence3_1, sentence3_2, sentence3_3,
        ])
        db.commit()
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(contracts_router)
app.include_router(clauses_router)
app.include_router(sentences_router)
