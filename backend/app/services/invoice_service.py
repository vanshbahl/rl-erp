from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.invoice import InvoiceStatusUpdate


class InvoiceService:

    @staticmethod
    def generate_invoice(db: Session, order_id: int, due_days: int) -> Invoice:
        if due_days <= 0:
            raise HTTPException(
                status_code=400,
                detail="Due days must be greater than zero"
            )

        order = InvoiceService._validate_order(db, order_id)
        
        # In this implementation, tax is 0 and total is subtotal
        subtotal, tax_amount, total_amount = InvoiceService._calculate_totals(order)

        from sqlalchemy.exc import IntegrityError

        for attempt in range(3):
            try:
                invoice_number = InvoiceService._generate_invoice_number(db)

                invoice = Invoice(
                    invoice_number=invoice_number,
                    order_id=order.id,
                    customer_id=order.customer_id,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    status="DRAFT",
                    due_date=datetime.utcnow() + timedelta(days=due_days)
                )

                db.add(invoice)
                db.flush()

                InvoiceService._create_invoice_items(db, invoice.id, order.id)

                db.commit()
                db.refresh(invoice)

                return invoice
            except IntegrityError:
                db.rollback()
                if attempt == 2:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to generate unique invoice number due to high concurrency"
                    )
            except Exception:
                db.rollback()
                raise

    @staticmethod
    def list_invoices(db: Session) -> list[Invoice]:
        return db.query(Invoice).all()

    @staticmethod
    def get_invoice(db: Session, invoice_id: int) -> tuple[Invoice, list[InvoiceItem]]:
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

        return invoice, items

    @staticmethod
    def transition_status(db: Session, invoice_id: int, status_data: InvoiceStatusUpdate) -> Invoice:
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

        new_status = status_data.status.upper()
        InvoiceService._validate_transition(invoice.status, new_status)

        try:
            invoice.status = new_status
            db.commit()
            db.refresh(invoice)
            return invoice
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _validate_order(db: Session, order_id: int) -> Order:
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

        return order

    @staticmethod
    def _generate_invoice_number(db: Session) -> str:
        last_invoice = db.query(Invoice).order_by(Invoice.id.desc()).first()
        if last_invoice and last_invoice.invoice_number.startswith("INV-"):
            try:
                last_num = int(last_invoice.invoice_number.split("-")[1])
                return f"INV-{(last_num + 1):06d}"
            except ValueError:
                pass
        return "INV-000001"

    @staticmethod
    def _calculate_totals(order: Order) -> tuple[float, float, float]:
        subtotal = order.total_amount
        tax_amount = 0.0
        total_amount = float(subtotal) + float(tax_amount)
        return subtotal, tax_amount, total_amount

    @staticmethod
    def _create_invoice_items(db: Session, invoice_id: int, order_id: int) -> None:
        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order_id)
            .all()
        )

        for item in order_items:
            db.add(
                InvoiceItem(
                    invoice_id=invoice_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    rate=item.rate,
                    amount=item.amount
                )
            )

    @staticmethod
    def _validate_transition(current_status: str, new_status: str) -> None:
        allowed_transitions = {
            "DRAFT": ["ISSUED", "CANCELLED"],
            "ISSUED": ["PARTIALLY_PAID", "PAID", "CANCELLED"],
            "PARTIALLY_PAID": ["PAID", "CANCELLED"],
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
