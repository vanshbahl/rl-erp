from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer

from app.schemas.payment import PaymentCreate

class PaymentService:

    @staticmethod
    def create_payment(db: Session, payment_data: PaymentCreate) -> Payment:
        try:
            invoice = (
                db.query(Invoice)
                .filter(Invoice.id == payment_data.invoice_id)
                .first()
            )

            if not invoice:
                raise HTTPException(
                    status_code=404,
                    detail="Invoice not found"
                )

            if invoice.status not in ["ISSUED", "PARTIALLY_PAID"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot record payment for invoice in status {invoice.status}"
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
        except Exception:
            db.rollback()
            raise


    @staticmethod
    def list_payments(db: Session) -> list[Payment]:
        return (
            db.query(Payment)
            .order_by(Payment.created_at.desc())
            .all()
        )

    @staticmethod
    def get_payment(db: Session, payment_id: int) -> Payment:
        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        return payment

    @staticmethod
    def invoice_summary(db: Session, invoice_id: int) -> dict:
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

    @staticmethod
    def customer_summary(db: Session, customer_id: int) -> dict:
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

        if not invoice_ids:
            paid_amount = 0
        else:
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

    @staticmethod
    def customer_invoices(db: Session, customer_id: int) -> dict:
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

    @staticmethod
    def outstanding_report(db: Session) -> list[dict]:
        invoices = db.query(Invoice).all()

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

            if outstanding_amount <= 0:
                continue

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id == invoice.customer_id
                )
                .first()
            )

            result.append({
                "customer_id": customer.id,
                "company_name": customer.company_name,
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "invoice_total": float(invoice.total_amount),
                "paid_amount": float(paid_amount),
                "outstanding_amount": outstanding_amount,
                "status": invoice.status
            })

        result.sort(
            key=lambda x: x["outstanding_amount"],
            reverse=True
        )

        return result

    @staticmethod
    def aging_report(db: Session) -> dict:
        invoices = db.query(Invoice).all()

        aging = {
            "current": 0,
            "0_30_days": 0,
            "31_60_days": 0,
            "61_90_days": 0,
            "90_plus_days": 0
        }

        invoice_details = []

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

            if outstanding_amount <= 0:
                continue

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id == invoice.customer_id
                )
                .first()
            )

            days_overdue = (
                datetime.utcnow()
                - invoice.due_date
            ).days

            if days_overdue < 0:
                aging["current"] += outstanding_amount
                bucket = "CURRENT"
            elif days_overdue <= 30:
                aging["0_30_days"] += outstanding_amount
                bucket = "0-30 DAYS"
            elif days_overdue <= 60:
                aging["31_60_days"] += outstanding_amount
                bucket = "31-60 DAYS"
            elif days_overdue <= 90:
                aging["61_90_days"] += outstanding_amount
                bucket = "61-90 DAYS"
            else:
                aging["90_plus_days"] += outstanding_amount
                bucket = "90+ DAYS"

            invoice_details.append({
                "customer_id": customer.id,
                "company_name": customer.company_name,
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "outstanding_amount": outstanding_amount,
                "days_overdue": max(days_overdue, 0),
                "bucket": bucket
            })

        return {
            "summary": aging,
            "invoices": invoice_details
        }
