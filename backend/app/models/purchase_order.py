from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric
)

from datetime import datetime

from app.core.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id")
    )

    contact_person = Column(String)

    po_number = Column(String)

    status = Column(
        String,
        default="DRAFT",
        nullable=False
    )

    remarks = Column(String)

    total_amount = Column(
        Numeric(14, 2),
        default=0
    )

    order_date = Column(
        DateTime,
        default=datetime.utcnow
    )