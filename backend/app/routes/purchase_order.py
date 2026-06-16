

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import require_roles
from app.models.enums import UserRole

from app.models.supplier import Supplier
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderStatusUpdate,
)


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

    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == po_data.supplier_id,
            Supplier.is_active == True
        )
        .first()
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    po_count = db.query(PurchaseOrder).count() + 1

    purchase_order = PurchaseOrder(
        supplier_id=po_data.supplier_id,
        contact_person=po_data.contact_person,
        po_number=f"PO-{po_count:06d}",
        remarks=po_data.remarks,
        status="DRAFT",
        total_amount=0
    )

    db.add(purchase_order)
    db.flush()

    total_amount = 0

    for item in po_data.items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        amount = float(item.quantity) * float(item.rate)

        po_item = PurchaseOrderItem(
            purchase_order_id=purchase_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            rate=item.rate,
            amount=amount
        )

        db.add(po_item)

        total_amount += amount

    purchase_order.total_amount = total_amount

    db.commit()
    db.refresh(purchase_order)

    items = (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.purchase_order_id == purchase_order.id
        )
        .all()
    )

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

    purchase_orders = (
        db.query(PurchaseOrder)
        .order_by(PurchaseOrder.id.desc())
        .all()
    )

    result = []

    for po in purchase_orders:

        items = (
            db.query(PurchaseOrderItem)
            .filter(
                PurchaseOrderItem.purchase_order_id == po.id
            )
            .all()
        )

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

    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found"
        )

    items = (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.purchase_order_id == purchase_order.id
        )
        .all()
    )

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

    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found"
        )

    allowed_statuses = [
        "DRAFT",
        "SENT",
        "PARTIALLY_RECEIVED",
        "RECEIVED",
        "CANCELLED"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of {allowed_statuses}"
        )

    purchase_order.status = status_data.status

    db.commit()

    return {
        "message": "Purchase order status updated successfully"
    }