"""Authentication fixtures: user creation and JWT token helpers."""

import pytest
from app.core.security import hash_password, create_access_token
from app.models.user import User


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin_user(db):
    user = User(
        username="test_admin",
        email="admin@test.com",
        hashed_password=hash_password("adminpass"),
        role="admin",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def manager_user(db):
    user = User(
        username="test_manager",
        email="manager@test.com",
        hashed_password=hash_password("managerpass"),
        role="manager",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture()
def staff_user(db):
    user = User(
        username="test_staff",
        email="staff@test.com",
        hashed_password=hash_password("staffpass"),
        role="staff",
    )
    db.add(user)
    db.flush()
    return user


# ---------------------------------------------------------------------------
# Token fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id)})


@pytest.fixture()
def manager_token(manager_user):
    return create_access_token({"sub": str(manager_user.id)})


@pytest.fixture()
def staff_token(staff_user):
    return create_access_token({"sub": str(staff_user.id)})


# ---------------------------------------------------------------------------
# Header fixtures — ready-to-use Authorization dicts
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def manager_headers(manager_token):
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture()
def staff_headers(staff_token):
    return {"Authorization": f"Bearer {staff_token}"}
