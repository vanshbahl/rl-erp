from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.bom import BOMCreate, BOMUpdate, BOMResponse
from app.services.bom_service import BOMService

router = APIRouter(
    prefix="/boms",
    tags=["Bill of Materials"]
)


@router.post("", response_model=BOMResponse)
def create_bom(
    bom_data: BOMCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    return BOMService.create_bom(db, bom_data)


@router.get("", response_model=list[BOMResponse])
def get_boms(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return BOMService.list_boms(db)


@router.get("/product/{product_id}", response_model=BOMResponse)
def get_active_bom_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return BOMService.get_active_bom_by_product(db, product_id)


@router.get("/{id}", response_model=BOMResponse)
def get_bom(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return BOMService.get_bom(db, id)


@router.put("/{id}", response_model=BOMResponse)
def update_bom(
    id: int,
    bom_data: BOMUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    return BOMService.update_bom(db, id, bom_data)


@router.patch("/{id}/activate", response_model=BOMResponse)
def activate_bom(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    return BOMService.activate_bom(db, id)
