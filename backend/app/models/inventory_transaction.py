from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=True,
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=True,
    )

    quantity_change = Column(
        Float,
        nullable=False,
    )

    transaction_type = Column(
        String,
        nullable=False,
    )

    remarks = Column(String)

    production_execution_id = Column(
        Integer,
        ForeignKey("production_executions.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    production_execution = relationship(
        "ProductionExecution",
        back_populates="inventory_transactions",
    )
