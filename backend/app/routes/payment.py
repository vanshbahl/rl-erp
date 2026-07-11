from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)

from app.services.payment_service import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGER
            )
        )
    ]
)

@router.post(
    "",
    response_model=PaymentResponse
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    payment = PaymentService.create_payment(db, payment_data)
    return payment


@router.get(
    "",
    response_model=list[PaymentResponse]
)
def get_payments(
    db: Session = Depends(get_db)
):
    return PaymentService.list_payments(db)


@router.get("/invoice/{invoice_id}/summary")
def get_invoice_payment_summary(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    return PaymentService.invoice_summary(db, invoice_id)


@router.get("/customer/{customer_id}/summary")
def get_customer_payment_summary(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return PaymentService.customer_summary(db, customer_id)


@router.get("/customer/{customer_id}/invoices")
def get_customer_invoices(
    customer_id: int,
    db: Session = Depends(get_db)
):
    return PaymentService.customer_invoices(db, customer_id)


@router.get("/outstanding")
def get_outstanding_invoices(
    db: Session = Depends(get_db)
):
    return PaymentService.outstanding_report(db)


@router.get("/aging-report")
def get_aging_report(
    db: Session = Depends(get_db)
):
    return PaymentService.aging_report(db)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    return PaymentService.get_payment(db, payment_id)