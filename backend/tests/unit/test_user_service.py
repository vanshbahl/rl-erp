from app.core.security import verify_password
from app.models.enums import UserRole
from app.models.user import User
from app.services.user_service import bootstrap_default_admin
from tests.factories.models import make_user


class TestDefaultAdminBootstrap:
    def test_creates_admin_once_and_preserves_password(self, db):
        user = bootstrap_default_admin(
            db,
            username="bootstrap_admin",
            email="bootstrap-admin@test.com",
            password="initial-password",
        )

        assert user is not None
        assert user.role == UserRole.ADMIN.value
        assert verify_password("initial-password", user.hashed_password)
        initial_hash = user.hashed_password

        second_user = bootstrap_default_admin(
            db,
            username="bootstrap_admin",
            email="bootstrap-admin@test.com",
            password="different-password",
        )

        assert second_user is not None
        assert second_user.id == user.id
        assert second_user.hashed_password == initial_hash
        assert db.query(User).filter(User.username == "bootstrap_admin").count() == 1

    def test_promotes_existing_user_without_resetting_password(self, db):
        user = make_user(
            db,
            username="future_admin",
            email="future-admin@test.com",
            role=UserRole.STAFF.value,
            password="existing-password",
        )
        initial_hash = user.hashed_password

        promoted_user = bootstrap_default_admin(
            db,
            username=user.username,
            email=user.email,
            password="new-bootstrap-password",
        )

        assert promoted_user is not None
        assert promoted_user.role == UserRole.ADMIN.value
        assert promoted_user.hashed_password == initial_hash
        assert verify_password("existing-password", promoted_user.hashed_password)

    def test_no_configuration_is_a_no_op(self, db):
        assert bootstrap_default_admin(db, "", "", "") is None
