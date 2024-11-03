import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Primary fixture for database session management
@pytest.fixture(scope="module", name="fakedb")
def override_get_db():
    # Set up the database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Fixture for the test client with dependency override
@pytest.fixture(scope="module")
def client(fakedb):
    app.dependency_overrides[get_db] = lambda: fakedb
    with TestClient(app) as test_app:
        yield test_app
