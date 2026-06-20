from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductionExecution(Base):
    __tablename__ = "production_executions"

    id = Column(Integer, primary_key=True, index=True)
    production_order_id = Column(
        Integer,
        ForeignKey("production_orders.id"),
        nullable=False
    )
    executed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    quantity_produced = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="COMPLETED")  # COMPLETED, ROLLED_BACK
    notes = Column(String, nullable=True)
    executed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    rolled_back_at = Column(
        DateTime,
        nullable=True
    )

    __table_args__ = (
        Index("idx_prod_exec_po_status", "production_order_id", "status"),
    )

    production_order = relationship("ProductionOrder")
    executor = relationship("User")
    items = relationship(
        "ProductionExecutionItem",
        back_populates="execution",
        cascade="all, delete-orphan"
    )
    inventory_transactions = relationship(
        "InventoryTransaction",
        back_populates="production_execution"
    )
