from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.invoice import InvoiceStatusUpdate

from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)


@router.post("/generate/{order_id}")
def generate_invoice(
    order_id: int,
    due_days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    invoice = InvoiceService.generate_invoice(db, order_id, due_days)

    return {
        "message": "Invoice generated successfully",
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number
    }


@router.get("")
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return InvoiceService.list_invoices(db)


@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    invoice, items = InvoiceService.get_invoice(db, invoice_id)

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
    invoice = InvoiceService.transition_status(db, invoice_id, status_data)

    return {
        "message": "Invoice status updated",
        "invoice": invoice
    }