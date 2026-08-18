from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import APP_ENV, DEFAULT_ADMIN_USERNAME, DEV_AUTH_BYPASS
from app.dependencies.auth import require_admin

from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate

from app.schemas.auth import LoginRequest, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email
    }


@router.post("/dev-login", response_model=Token)
def dev_login(db: Session = Depends(get_db)):
    if APP_ENV != "development" or not DEV_AUTH_BYPASS:
        raise HTTPException(status_code=404, detail="Not found")

    user = db.query(User).filter(
        User.username == DEFAULT_ADMIN_USERNAME,
        User.role == UserRole.ADMIN.value,
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "token_type": "bearer",
    }

@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    if not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
