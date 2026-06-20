from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductionOrderItem(Base):
    __tablename__ = "production_order_items"

    id = Column(Integer, primary_key=True, index=True)
    production_order_id = Column(
        Integer,
        ForeignKey("production_orders.id", ondelete="CASCADE"),
        nullable=False
    )
    component_product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    quantity_required = Column(Float, nullable=False)
    unit_of_measure = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "production_order_id",
            "component_product_id",
            name="uq_po_items_po_component"
        ),
    )

    production_order = relationship("ProductionOrder", back_populates="items")
    component = relationship("Product")
