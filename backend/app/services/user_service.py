from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User


def bootstrap_default_admin(
    db: Session,
    username: str,
    email: str,
    password: str,
) -> User | None:
    if not username or not email or not password:
        return None

    matching_users = db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).all()

    if len(matching_users) > 1:
        raise ValueError(
            "Default admin username and email belong to different users"
        )

    if matching_users:
        user = matching_users[0]
        if user.role != UserRole.ADMIN.value:
            user.role = UserRole.ADMIN.value
            db.commit()
            db.refresh(user)
        return user

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.ADMIN.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
