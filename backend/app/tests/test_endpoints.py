import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base, Clause, Contract, Sentence

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_upload_contract_success():
    file_content = b"This is sentence one. This is sentence two."
    file = {"file": ("contract.txt", file_content, "text/plain")}

    response = client.post("/contracts/", files=file)

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "contract.txt"
    assert "id" in data
    assert len(data["sentences"]) == 2


def test_upload_contract_invalid_extension():
    file = {"file": ("contract.pdf", b"Some pdf content", "application/pdf")}

    response = client.post("/contracts/", files=file)

    assert response.status_code == 415
    assert response.json()["detail"] == "Only .txt and .md files are accepted."


def test_get_contract_success():
    with TestingSessionLocal() as db:
        contract_id = uuid.uuid4()
        db.add(Contract(id=contract_id, filename="test.txt", raw_text="Hello world."))
        db.commit()

    response = client.get(f"/contracts/{contract_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["id"] == str(contract_id)


def test_get_contract_not_found():
    response = client.get(f"/contracts/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found."


def test_get_dashboard_returns_all_contracts():
    with TestingSessionLocal() as db:
        db.add(Contract(id=uuid.uuid4(), filename="contract_a.txt", raw_text="..."))
        db.add(Contract(id=uuid.uuid4(), filename="contract_b.txt", raw_text="..."))
        db.commit()

    response = client.get("/contracts/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_dashboard_search_filter():
    with TestingSessionLocal() as db:
        db.add(Contract(id=uuid.uuid4(), filename="employment_contract.txt", raw_text="..."))
        db.add(Contract(id=uuid.uuid4(), filename="lease_agreement.txt", raw_text="..."))
        db.commit()

    response = client.get("/contracts/", params={"search": "lease"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "lease_agreement.txt"


def test_get_dashboard_clause_id_filter():
    with TestingSessionLocal() as db:
        clause_id = uuid.uuid4()
        db.add(Clause(id=clause_id, name="Non-Compete"))

        contract_id = uuid.uuid4()
        db.add(Contract(id=contract_id, filename="labeled.txt", raw_text="..."))
        db.add(Sentence(id=uuid.uuid4(), contract_id=contract_id, text="...", position=0, label_id=clause_id))
        db.add(Contract(id=uuid.uuid4(), filename="unlabeled.txt", raw_text="..."))
        db.commit()

    response = client.get("/contracts/", params={"clause_id": str(clause_id)})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "labeled.txt"


# --- /clauses ---

def test_get_clauses_empty():
    response = client.get("/clauses/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_clauses_returns_all():
    with TestingSessionLocal() as db:
        db.add(Clause(id=uuid.uuid4(), name="Non-Compete", color="#ff0000"))
        db.add(Clause(id=uuid.uuid4(), name="Termination for Convenience", color="#00ff00"))
        db.commit()

    response = client.get("/clauses/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {c["name"] for c in data} == {"Non-Compete", "Termination for Convenience"}


# --- /sentences ---

def test_update_sentence_label_success():
    with TestingSessionLocal() as db:
        clause_id = uuid.uuid4()
        db.add(Clause(id=clause_id, name="Limitation of Liability", color="#ff0000"))

        contract_id = uuid.uuid4()
        db.add(Contract(id=contract_id, filename="test.txt", raw_text="Some text."))

        sentence_id = uuid.uuid4()
        db.add(Sentence(id=sentence_id, contract_id=contract_id, text="Some text.", position=0))
        db.commit()

    response = client.patch(f"/sentences/{sentence_id}", json={"clause_id": str(clause_id)})

    assert response.status_code == 200
    data = response.json()
    assert data["label_name"] == "Limitation of Liability"
    assert data["label_color"] == "#ff0000"


def test_update_sentence_label_remove():
    with TestingSessionLocal() as db:
        clause_id = uuid.uuid4()
        db.add(Clause(id=clause_id, name="Non-Compete"))

        contract_id = uuid.uuid4()
        db.add(Contract(id=contract_id, filename="test.txt", raw_text="Some text."))

        sentence_id = uuid.uuid4()
        db.add(Sentence(id=sentence_id, contract_id=contract_id, text="Some text.", position=0, label_id=clause_id))
        db.commit()

    response = client.patch(f"/sentences/{sentence_id}", json={"clause_id": None})

    assert response.status_code == 200
    data = response.json()
    assert data["label_name"] is None
    assert data["label_color"] is None


def test_update_sentence_label_sentence_not_found():
    response = client.patch(f"/sentences/{uuid.uuid4()}", json={"clause_id": None})

    assert response.status_code == 404
    assert response.json()["detail"] == "Sentence not found."


def test_update_sentence_label_clause_not_found():
    with TestingSessionLocal() as db:
        contract_id = uuid.uuid4()
        db.add(Contract(id=contract_id, filename="test.txt", raw_text="Some text."))

        sentence_id = uuid.uuid4()
        db.add(Sentence(id=sentence_id, contract_id=contract_id, text="Some text.", position=0))
        db.commit()

    response = client.patch(f"/sentences/{sentence_id}", json={"clause_id": str(uuid.uuid4())})

    assert response.status_code == 404
    assert response.json()["detail"] == "Clause not found."
