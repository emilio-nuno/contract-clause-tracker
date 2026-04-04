import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Contract, Base

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
    file  = {"file": ("contract.txt", file_content, "text/plain")}
    
    response = client.post("/contracts", files=file)
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "contract.txt"
    assert "id" in data
    assert len(data["sentences"]) == 2 


def test_upload_contract_invalid_extension():
    file = {"file": ("contract.pdf", b"Some pdf content", "application/pdf")}
    
    response = client.post("/contracts", files=file)
    
    assert response.status_code == 415
    assert response.json()["detail"] == "Only .txt and .md files are accepted."



def test_get_contract_success():
    with TestingSessionLocal() as db:
        contract_id = uuid.uuid4()
        dummy_contract = Contract(id=contract_id, filename="test.txt", raw_text="Hello world.")
        db.add(dummy_contract)
        db.commit()
    
    response = client.get(f"/contracts/{contract_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["id"] == str(contract_id)


def test_get_contract_not_found():
    random_uuid = uuid.uuid4()
    response = client.get(f"/contracts/{random_uuid}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found."



def test_get_dashboard_search_filter():
    with TestingSessionLocal() as db:
        db.add(Contract(id=uuid.uuid4(), filename="employment_contract.txt", raw_text="..."))
        db.add(Contract(id=uuid.uuid4(), filename="lease_agreement.txt", raw_text="..."))
        db.commit()
    
    response = client.get("/contracts", params={"search": "lease"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "lease_agreement.txt"