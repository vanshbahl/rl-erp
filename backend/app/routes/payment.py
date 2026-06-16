from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import require_roles
from app.models.enums import UserRole

from app.models.payment import Payment
from app.models.invoice import Invoice

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)

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
    db: Session = Depends(get_db),
    
    ):

    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == payment_data.invoice_id
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    if payment_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than zero"
        )

    allowed_methods = [
        "CASH",
        "BANK_TRANSFER",
        "CHEQUE",
        "UPI",
        "CARD"
    ]

    if payment_data.payment_method.upper() not in allowed_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Payment method must be one of {allowed_methods}"
        )

    payment = Payment(
        invoice_id=payment_data.invoice_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method.upper(),
        reference_number=payment_data.reference_number,
        remarks=payment_data.remarks
    )

    db.add(payment)

    db.commit()
    db.refresh(payment)

    return payment


@router.get(
    "",
    response_model=list[PaymentResponse]
)
def get_payments(
    db: Session = Depends(get_db)
):
    return (
        db.query(Payment)
        .order_by(Payment.created_at.desc())
        .all()
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):

    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment