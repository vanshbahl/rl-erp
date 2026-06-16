from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.invoice import InvoiceStatusUpdate

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)


@router.post("/generate/{order_id}")
def generate_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_statuses = ["DISPATCHED", "COMPLETED"]

    if order.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invoices can only be generated for dispatched or completed orders"
        )

    existing_invoice = (
        db.query(Invoice)
        .filter(Invoice.order_id == order.id)
        .first()
    )

    if existing_invoice:
        raise HTTPException(
            status_code=400,
            detail="Invoice already exists for this order"
        )

    invoice_count = db.query(Invoice).count() + 1

    invoice = Invoice(
        invoice_number=f"INV-{invoice_count:06d}",
        order_id=order.id,
        customer_id=order.customer_id,
        subtotal=order.total_amount,
        tax_amount=0,
        total_amount=order.total_amount,
        status="DRAFT"
    )

    db.add(invoice)
    db.flush()

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    for item in order_items:
        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                quantity=item.quantity,
                rate=item.rate,
                amount=item.amount
            )
        )

    db.commit()
    db.refresh(invoice)

    return {
        "message": "Invoice generated successfully",
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number
    }


@router.get("")
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    items = (
        db.query(InvoiceItem)
        .filter(InvoiceItem.invoice_id == invoice.id)
        .all()
    )

    return {
        "invoice": invoice,
        "items": items
    }


@router.patch("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: int,
    status_data: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
            
        )
    )
):

    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    current_status = invoice.status
    new_status = status_data.status.upper()

    allowed_transitions = {
        "DRAFT": ["ISSUED", "CANCELLED"],
        "ISSUED": ["PAID", "CANCELLED"],
        "PAID": [],
        "CANCELLED": []
    }

    if current_status not in allowed_transitions:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown current invoice status: {current_status}"
        )

    if new_status == current_status:
        raise HTTPException(
            status_code=400,
            detail="Invoice is already in that status"
        )

    if new_status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )

    invoice.status = new_status

    db.commit()
    db.refresh(invoice)

    return {
        "message": "Invoice status updated",
        "invoice": invoice
    }