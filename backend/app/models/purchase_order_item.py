from sqlalchemy import (
    Column,
    Integer,
    Float,
    Numeric,
    ForeignKey
)

from app.core.database import Base


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity = Column(Float)

    received_quantity = Column(
    Float,
    default=0,
    nullable=False
    )

    rate = Column(Numeric(12, 2))

    amount = Column(Numeric(14, 2))