"""
Root conftest.py — database engine, session, and app-level fixtures.

Design decisions:
- Uses a dedicated test database (rlerp_test) to avoid touching production data.
- Each test function gets a fresh rolled-back transaction so tests are
  fully isolated without recreating the schema on every run.
- The FastAPI dependency override for get_db is applied here once so
  every test client uses the isolated session automatically.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set the test database URL BEFORE any application modules are imported
# so config.py / database.py pick up the test DSN.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://localhost/rlerp_test"
)

from app.core.database import Base  # noqa: E402 — must come after env setup
from main import app as main_app    # noqa: E402
from app.core.database import get_db  # noqa: E402

import app.models  # noqa: E402 — registers all ORM models with Base

# ---------------------------------------------------------------------------
# Database engine — created once per process
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Schema fixture — creates all tables once per test session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_schema():
    """Create all tables before the test session; drop them afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Isolated database session — rolls back after each test
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    """
    Yields a SQLAlchemy Session that is rolled back after the test.

    Each test operates inside a transaction that is never committed to
    the database; the rollback at the end leaves the schema pristine for
    the next test.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(db):
    """
    Returns a TestClient whose requests use the isolated test session.

    The FastAPI dependency `get_db` is overridden to inject the test
    session instead of the production session, so every service called
    through the HTTP layer operates inside the same rolled-back
    transaction as the test.
    """
    def override_get_db():
        yield db

    main_app.dependency_overrides[get_db] = override_get_db
    with TestClient(main_app) as c:
        yield c
    main_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Authentication fixtures (re-exported from fixtures/auth.py)
# ---------------------------------------------------------------------------

from tests.fixtures.auth import (  # noqa: E402, F401
    admin_user,
    manager_user,
    staff_user,
    admin_token,
    manager_token,
    staff_token,
    admin_headers,
    manager_headers,
    staff_headers,
)
