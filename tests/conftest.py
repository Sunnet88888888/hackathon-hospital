import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import get_password_hash

# Create in-memory SQLite database engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True, scope="function")
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after test completes
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def admin_headers(client):
    db = TestingSessionLocal()
    db.add(User(
        email="admin@clinic.com",
        password_hash=get_password_hash("adminpassword123"),
        full_name="Clinic Admin",
        role="admin"
    ))
    db.commit()
    db.close()

    login_response = client.post("/auth/login", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123"
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
