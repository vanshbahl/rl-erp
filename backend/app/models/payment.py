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


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=False
    )

    amount = Column(
        Numeric(14, 2),
        nullable=False
    )

    payment_method = Column(
        String,
        nullable=False
    )

    reference_number = Column(
        String,
        nullable=True
    )

    remarks = Column(
        String,
        nullable=True
    )

    payment_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )