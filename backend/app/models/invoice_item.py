from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
)

from app.core.database import Base


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=False,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )

    quantity = Column(
        Numeric(14, 2),
        nullable=False,
    )

    rate = Column(
        Numeric(14, 2),
        nullable=False,
    )

    amount = Column(
        Numeric(14, 2),
        nullable=False,
    )