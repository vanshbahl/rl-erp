from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db


from app.dependencies.auth import require_roles
from app.models.enums import UserRole

from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer

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

    already_paid = (
        db.query(
            func.coalesce(
                func.sum(Payment.amount),
                0
            )
        )
        .filter(
            Payment.invoice_id == invoice.id
        )
        .scalar()
    )

    remaining_balance = (
        float(invoice.total_amount)
        - float(already_paid)
    )

    if payment_data.amount > remaining_balance:
        raise HTTPException(
            status_code=400,
            detail="Payment exceeds outstanding balance"
        )

    payment = Payment(
        invoice_id=payment_data.invoice_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method.upper(),
        reference_number=payment_data.reference_number,
        remarks=payment_data.remarks
    )

    db.add(payment)

    new_paid_amount = (
        float(already_paid)
        + float(payment_data.amount)
    )

    outstanding_balance = (
        float(invoice.total_amount)
        - new_paid_amount
    )

    if outstanding_balance <= 0:
        invoice.status = "PAID"
    else:
        invoice.status = "PARTIALLY_PAID"

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


# New endpoint for invoice payment summary
@router.get("/invoice/{invoice_id}/summary")
def get_invoice_payment_summary(
    invoice_id: int,
    db: Session = Depends(get_db)
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

    paid_amount = (
        db.query(
            func.coalesce(
                func.sum(Payment.amount),
                0
            )
        )
        .filter(
            Payment.invoice_id == invoice.id
        )
        .scalar()
    )

    outstanding_amount = (
        float(invoice.total_amount)
        - float(paid_amount)
    )

    return {
        "invoice_id": invoice.id,
        "invoice_total": float(invoice.total_amount),
        "paid_amount": float(paid_amount),
        "outstanding_amount": outstanding_amount,
        "status": invoice.status
    }

@router.get("/customer/{customer_id}/summary")
def get_customer_payment_summary(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    invoices = (
        db.query(Invoice)
        .filter(
            Invoice.customer_id == customer_id
        )
        .all()
    )

    total_invoiced = sum(
        float(invoice.total_amount)
        for invoice in invoices
    )

    invoice_ids = [
        invoice.id
        for invoice in invoices
    ]

    paid_amount = (
        db.query(
            func.coalesce(
                func.sum(Payment.amount),
                0
            )
        )
        .filter(
            Payment.invoice_id.in_(invoice_ids)
        )
        .scalar()
    )

    outstanding_amount = (
        total_invoiced
        - float(paid_amount)
    )

    return {
        "customer_id": customer.id,
        "company_name": customer.company_name,
        "total_invoiced": total_invoiced,
        "total_paid": float(paid_amount),
        "outstanding_amount": outstanding_amount
    }

@router.get("/customer/{customer_id}/invoices")
def get_customer_invoices(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    invoices = (
        db.query(Invoice)
        .filter(Invoice.customer_id == customer_id)
        .order_by(Invoice.created_at.desc())
        .all()
    )

    result = []

    for invoice in invoices:

        paid_amount = (
            db.query(
                func.coalesce(
                    func.sum(Payment.amount),
                    0
                )
            )
            .filter(
                Payment.invoice_id == invoice.id
            )
            .scalar()
        )

        outstanding_amount = (
            float(invoice.total_amount)
            - float(paid_amount)
        )

        result.append({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_total": float(invoice.total_amount),
            "paid_amount": float(paid_amount),
            "outstanding_amount": outstanding_amount,
            "status": invoice.status
        })

    return {
        "customer_id": customer.id,
        "company_name": customer.company_name,
        "invoices": result
    }