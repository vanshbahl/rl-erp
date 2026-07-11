"""
Smoke test — validates that the test infrastructure itself works correctly.

These tests do NOT test application logic.
They verify that:
- The test database is reachable
- Schema creation succeeds
- The FastAPI test client starts correctly
- The db fixture rollback is working (no data leaks between tests)
- Auth fixtures produce valid tokens accepted by the API
"""

import pytest


@pytest.mark.unit
class TestInfrastructureSmoke:

    def test_health_endpoint_is_reachable(self, client):
        """The test client can reach the running FastAPI app."""
        response = client.get("/Health")
        assert response.status_code == 200

    def test_db_fixture_provides_session(self, db):
        """The db fixture yields a usable SQLAlchemy session."""
        from app.models.user import User
        count = db.query(User).count()
        assert isinstance(count, int)

    def test_admin_token_is_accepted_by_protected_endpoint(self, client, admin_headers):
        """Admin JWT is accepted by an authenticated endpoint."""
        response = client.get("/invoices", headers=admin_headers)
        # 200 = authenticated successfully (may return empty list)
        # 404 = route missing (infra problem)
        assert response.status_code in (200, 422), (
            f"Unexpected status {response.status_code}: {response.text}"
        )

    def test_unauthenticated_request_is_rejected(self, client):
        """A protected endpoint without a token returns 401 or 403."""
        response = client.get("/invoices")
        assert response.status_code in (401, 403)

    def test_db_isolation_write_first(self, db):
        """Write a user — must not be visible in subsequent isolated test."""
        from tests.factories.models import make_user
        user = make_user(db, username="isolation_test_user", email="iso@test.com")
        assert user.id is not None

    def test_db_isolation_read_second(self, db):
        """isolation_test_user from the previous test must not exist here."""
        from app.models.user import User
        user = db.query(User).filter(User.username == "isolation_test_user").first()
        assert user is None, (
            "Test isolation is broken — data from a previous test is visible"
        )
