from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
)

from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(
        String,
        unique=True,
        nullable=False,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
    )

    subtotal = Column(
        Numeric(14, 2),
        default=0,
    )

    tax_amount = Column(
        Numeric(14, 2),
        default=0,
    )

    total_amount = Column(
        Numeric(14, 2),
        default=0,
    )

    status = Column(
        String,
        default="DRAFT",
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )