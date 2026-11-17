import os

# Use in-memory SQLite + mock LLM for all tests (no local .db files)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["MOCK_LLM"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app


# In-memory SQLite so tests don't touch the real DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


SAMPLE_LESSON = (
    "Plants need sunlight, water and soil to grow. "
    "Leaves help plants make food. Roots take water from the soil. "
    "The stem helps the plant stand upright."
)
