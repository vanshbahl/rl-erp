"""
Comprehensive test suite for Authentication and Security.
Covers:
- Registration (success, duplicate)
- Login (success, invalid credentials)
- JWT Creation & Validation
- Expired & Invalid Tokens
- Role Validation & Protected Routes
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import SECRET_KEY, ALGORITHM
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)
from app.dependencies.auth import get_current_user, require_admin, require_roles
from app.models.enums import UserRole
from app.models.user import User


@pytest.mark.security
class TestAuthenticationEndpoints:

    def test_register_success(self, client, db):
        payload = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "securepassword123"
        }
        response = client.post("/auth/register", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert "id" in data
        
        # Verify in DB
        user = db.query(User).filter(User.email == "newuser@test.com").first()
        assert user is not None
        assert verify_password("securepassword123", user.hashed_password)

    def test_register_duplicate_email(self, client, staff_user):
        payload = {
            "username": "duplicate",
            "email": staff_user.email,  # Already exists
            "password": "securepassword123"
        }
        response = client.post("/auth/register", json=payload)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_success(self, client, staff_user):
        payload = {
            "email": staff_user.email,
            "password": "staffpass" # from fixtures/auth.py
        }
        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client):
        payload = {
            "email": "doesnotexist@test.com",
            "password": "somepassword"
        }
        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client, staff_user):
        payload = {
            "email": staff_user.email,
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()


@pytest.mark.security
class TestSecurityCore:

    def test_hash_and_verify_password(self):
        password = "mysecretpassword"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_create_and_verify_token(self):
        data = {"sub": "1234"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "1234"
        assert "exp" in payload

    def test_verify_expired_token(self):
        # Create an expired token manually
        to_encode = {"sub": "1234"}
        expire = datetime.utcnow() - timedelta(minutes=15)
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Verify should return None for expired tokens
        payload = verify_token(token)
        assert payload is None

    def test_verify_invalid_token(self):
        # Malformed token
        assert verify_token("not.a.real.token") is None
        
        # Signed with wrong key
        token = jwt.encode({"sub": "123"}, "wrong-secret-key", algorithm=ALGORITHM)
        assert verify_token(token) is None


@pytest.mark.security
class TestAuthDependencies:

    def test_get_current_user_invalid_token(self, db):
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token")
        
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=creds, db=db)
            
        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid token"

    def test_get_current_user_not_found(self, db):
        token = create_access_token({"sub": "999999"})
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=creds, db=db)
            
        assert exc.value.status_code == 401
        assert exc.value.detail == "User not found"

    def test_get_current_user_success(self, db, admin_user, admin_token):
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=admin_token)
        user = get_current_user(credentials=creds, db=db)
        
        assert user.id == admin_user.id
        assert user.email == admin_user.email

    def test_require_admin_success(self, admin_user):
        user = require_admin(current_user=admin_user)
        assert user == admin_user

    def test_require_admin_forbidden(self, staff_user):
        with pytest.raises(HTTPException) as exc:
            require_admin(current_user=staff_user)
            
        assert exc.value.status_code == 403
        assert exc.value.detail == "Admin access required"

    def test_require_roles_success(self, manager_user):
        checker = require_roles(UserRole.MANAGER, UserRole.ADMIN)
        user = checker(current_user=manager_user)
        assert user == manager_user

    def test_require_roles_forbidden(self, staff_user):
        checker = require_roles(UserRole.ADMIN, UserRole.MANAGER)
        
        with pytest.raises(HTTPException) as exc:
            checker(current_user=staff_user)
            
        assert exc.value.status_code == 403
        assert exc.value.detail == "Insufficient permissions"


@pytest.mark.security
class TestProtectedRoutes:

    def test_protected_route_without_token(self, client):
        # /invoices requires authentication
        response = client.get("/invoices")
        assert response.status_code in (401, 403), f"Expected 401 or 403, got {response.status_code}"

    def test_protected_route_with_invalid_token(self, client):
        response = client.get("/invoices", headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"
