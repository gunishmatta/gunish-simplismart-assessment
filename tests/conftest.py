from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_db
from app.main import app

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

# Test setup
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    with engine.connect() as connection:
        with connection.begin():
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client() -> Generator:
	def override_get_db():
		try:
			db = TestingSessionLocal()
			yield db
		finally:
			db.close()

	# Override the dependency
	app.dependency_overrides[get_db] = override_get_db

	# Provide the test client
	with TestClient(app) as c:
		yield c
