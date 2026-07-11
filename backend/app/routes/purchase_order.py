from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderStatusUpdate,
    PurchaseOrderReceive,
)

from app.services.purchase_order_service import PurchaseOrderService


router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGER,
            )
        )
    ]
)


@router.post(
    "",
    response_model=PurchaseOrderResponse
)
def create_purchase_order(
    po_data: PurchaseOrderCreate,
    db: Session = Depends(get_db)
):
    purchase_order = PurchaseOrderService.create_purchase_order(db, po_data)
    items = PurchaseOrderService.get_items_for_purchase_order(db, purchase_order.id)

    return {
        "id": purchase_order.id,
        "supplier_id": purchase_order.supplier_id,
        "contact_person": purchase_order.contact_person,
        "po_number": purchase_order.po_number,
        "status": purchase_order.status,
        "remarks": purchase_order.remarks,
        "total_amount": float(purchase_order.total_amount),
        "items": items
    }


@router.get(
    "",
    response_model=list[PurchaseOrderResponse]
)
def get_purchase_orders(
    db: Session = Depends(get_db)
):
    purchase_orders = PurchaseOrderService.list_purchase_orders(db)

    result = []
    for po in purchase_orders:
        items = PurchaseOrderService.get_items_for_purchase_order(db, po.id)
        result.append({
            "id": po.id,
            "supplier_id": po.supplier_id,
            "contact_person": po.contact_person,
            "po_number": po.po_number,
            "status": po.status,
            "remarks": po.remarks,
            "total_amount": float(po.total_amount),
            "items": items
        })

    return result


@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse
)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db)
):
    purchase_order, items = PurchaseOrderService.get_purchase_order(db, purchase_order_id)

    return {
        "id": purchase_order.id,
        "supplier_id": purchase_order.supplier_id,
        "contact_person": purchase_order.contact_person,
        "po_number": purchase_order.po_number,
        "status": purchase_order.status,
        "remarks": purchase_order.remarks,
        "total_amount": float(purchase_order.total_amount),
        "items": items
    }


@router.patch("/{purchase_order_id}/status")
def update_purchase_order_status(
    purchase_order_id: int,
    status_data: PurchaseOrderStatusUpdate,
    db: Session = Depends(get_db)
):
    PurchaseOrderService.transition_status(db, purchase_order_id, status_data)

    return {
        "message": "Purchase order status updated successfully"
    }


@router.post("/{purchase_order_id}/receive")
def receive_purchase_order(
    purchase_order_id: int,
    receive_data: PurchaseOrderReceive,
    db: Session = Depends(get_db)
):
    purchase_order = PurchaseOrderService.receive_goods(db, purchase_order_id, receive_data)

    return {
        "message": "Purchase order received successfully",
        "status": purchase_order.status
    }