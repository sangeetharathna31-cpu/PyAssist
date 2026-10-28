import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_pyassist.db"

from pyassist.app.main import app
from pyassist.app.database import Base, get_db
from pyassist.app.auth import reset_rate_limits

# Create test engine and session
test_engine = create_engine(
    "sqlite:///./test_pyassist.db",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def clean_database_per_test():
    """Wipe and re-create database tables before every test function for strict isolation."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    reset_rate_limits()
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def db_session():
    """Direct database session fixture."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def registered_user(client):
    """Fixture that registers a standard test user and returns credentials and auth cookie."""
    user_data = {
        "username": "py_intern",
        "email": "intern@example.com",
        "password": "Password123"
    }
    res = client.post("/api/auth/register", json=user_data)
    assert res.status_code == 201, f"Failed registration in fixture: {res.text}"
    cookies = res.cookies
    return {
        "user": res.json(),
        "cookies": cookies,
        "credentials": user_data
    }

@pytest.fixture
def second_user(client):
    """Fixture that registers a second independent test user."""
    user_data = {
        "username": "second_coder",
        "email": "coder2@example.com",
        "password": "Password456"
    }
    res = client.post("/api/auth/register", json=user_data)
    assert res.status_code == 201
    return {
        "user": res.json(),
        "cookies": res.cookies,
        "credentials": user_data
    }
