from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.services.inventory_service import InventoryService

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get("/")
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return InventoryService.get_inventory(db)


@router.get("/low-stock")
def get_low_stock(
    product_type: str | None = None,
    supplier_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return InventoryService.get_low_stock(db, product_type, supplier_id)


@router.get("/{product_id}")
def get_inventory_item(
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
    return InventoryService.get_inventory_item(db, product_id)


@router.post("/")
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN
        )
    )
):
    return InventoryService.create_inventory(db, inventory)


@router.put("/{product_id}")
def update_inventory(
    product_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    return InventoryService.update_inventory(db, product_id, inventory_data)
