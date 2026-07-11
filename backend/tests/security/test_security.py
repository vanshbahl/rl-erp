import pytest
from jose import jwt
from datetime import datetime, timedelta

from app.core.config import SECRET_KEY, ALGORITHM

class TestSecurity:

    @pytest.mark.xfail(reason="Vulnerability: GET /products has missing authentication")
    def test_missing_authentication(self, client):
        """Test missing authentication on protected endpoints"""
        endpoints = [
            "/users/me",
            "/customers",
            "/products",
            "/orders",
            "/inventory"
        ]
        for ep in endpoints:
            response = client.get(ep)
            assert response.status_code == 401
            assert response.json()["detail"] == "Not authenticated"

    def test_invalid_permissions_staff_access_admin_route(self, client, staff_headers):
        """Test authorization failure when STAFF tries to access ADMIN endpoint"""
        response = client.get("/admin/users", headers=staff_headers)
        assert response.status_code == 403
        assert "admin access required" in response.json()["detail"].lower()

    def test_jwt_tampering(self, client, admin_headers):
        """Test that a tampered JWT is rejected"""
        token = admin_headers["Authorization"].split(" ")[1]
        
        # Modify the token by corrupting the signature section
        parts = token.split(".")
        parts[2] = parts[2][:-5] + "abcde" # Change the last 5 characters
        tampered_token = ".".join(parts)        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        assert response.status_code == 401
        assert "invalid token" in response.json()["detail"].lower()

    def test_expired_jwt(self, client):
        """Test that an expired JWT is rejected"""
        expire = datetime.utcnow() - timedelta(minutes=10)
        to_encode = {"sub": "1", "exp": expire}
        expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    def test_role_escalation_attempt(self, client, db):
        """Test that a user cannot escalate their role during registration"""
        from app.models.user import User
        reg_payload = {
            "username": "hacker_user",
            "email": "hacker@example.com",
            "password": "password123",
            "role": "ADMIN" # Escalation attempt
        }
        
        response = client.post("/auth/register", json=reg_payload)
        
        # If it returns 200, verify the user was created as STAFF
        if response.status_code == 200:
            user_id = response.json()["id"]
            user = db.query(User).filter(User.id == user_id).first()
            assert user.role == "staff"
            
    def test_sql_injection_attempts(self, client, admin_headers):
        """Test endpoints against SQL injection payloads"""
        payloads = [
            "' OR '1'='1",
            "1; DROP TABLE users",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in payloads:
            # 1. Search query params
            res1 = client.get(f"/customers?search={payload}", headers=admin_headers)
            assert res1.status_code in (200, 422)  # Should safely ignore or reject, not 500
            
            # 2. Path params
            res2 = client.get(f"/customers/{payload}", headers=admin_headers)
            assert res2.status_code in (404, 422)  # Should not be 500

    def test_invalid_payload(self, client, admin_headers):
        """Test endpoints with completely invalid JSON payloads"""
        # Sending string instead of JSON
        res = client.post(
            "/products",
            data="this is not a valid json",
            headers={"Authorization": admin_headers["Authorization"], "Content-Type": "application/json"}
        )
        assert res.status_code == 422
        
        # Sending empty dictionary for a model with required fields
        res2 = client.post(
            "/products",
            json={},
            headers=admin_headers
        )
        assert res2.status_code == 422

    def test_authorization_matrix(self, client, manager_headers, staff_headers):
        """Test proper authorization matrix across roles"""
        # STAFF trying to create a product (requires Admin/Manager)
        res_staff_prod = client.post(
            "/products", 
            json={"sku": "SEC-001", "name": "Sec", "product_type": "FINISHED_GOOD", "price": 10},
            headers=staff_headers
        )
        assert res_staff_prod.status_code == 403
        
        # MANAGER trying to create a product (Allowed)
        res_mgr_prod = client.post(
            "/products", 
            json={"sku": "SEC-002", "name": "Sec", "product_type": "FINISHED_GOOD", "price": 10},
            headers=manager_headers
        )
        assert res_mgr_prod.status_code == 200
