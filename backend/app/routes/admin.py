from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.core.database import get_db
from app.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: UserRole,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = role.value

    db.commit()
    db.refresh(user)

    return {
        "message": "Role updated",
        "user": user.username,
        "role": user.role
    }