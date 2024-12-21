from typing import Generator

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

# Test setup
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db() -> Generator:
	Base.metadata.create_all(bind=engine)
	yield TestingSessionLocal()
	Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client() -> Generator:
	def override_get_db():
		try:
			db = TestingSessionLocal()
			yield db
		finally:
			db.close()

	app.dependency_overrides[get_db] = override_get_db
	with TestClient(app) as c:
		yield c