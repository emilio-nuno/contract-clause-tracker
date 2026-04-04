from fastapi import FastAPI

from app.routers.contracts import router as contracts_router

app = FastAPI()

app.include_router(
    contracts_router
)

@app.get("/")
def root():
    return {"message": "Hello World"}