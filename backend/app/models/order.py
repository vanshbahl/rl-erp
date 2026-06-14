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


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id")
    )

    contact_person = Column(String)

    po_number = Column(String)

    status = Column(
    String,
    default="PENDING",
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
    
