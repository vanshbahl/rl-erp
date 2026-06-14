from sqlalchemy import (
    Column,
    Integer,
    Float,
    Numeric,
    ForeignKey
)

from app.core.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity = Column(Float)

    rate = Column(Numeric(12, 2))

    amount = Column(Numeric(14, 2))