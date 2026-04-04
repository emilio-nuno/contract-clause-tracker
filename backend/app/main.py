from fastapi import FastAPI

from app.routers.clauses import router as clauses_router
from app.routers.contracts import router as contracts_router
from app.routers.sentences import router as sentences_router

app = FastAPI()

app.include_router(contracts_router)
app.include_router(clauses_router)
app.include_router(sentences_router)


@app.get("/")
def root():
    return {"message": "Hello World"}
