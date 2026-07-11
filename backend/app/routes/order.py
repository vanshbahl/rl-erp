from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.order import (
    OrderCreate,
    OrderStatusUpdate
)

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.models.user import User

from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    order = OrderService.create_order(db, order_data)

    return {
        "message": "Order created successfully",
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
    }


@router.get("/")
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return OrderService.list_orders(db)


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    order, items = OrderService.get_order(db, order_id)

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": items
    }


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    order = OrderService.transition_status(db, order_id, status_data)

    return {
        "message": "Order status updated",
        "order_id": order.id,
        "status": order.status
    }