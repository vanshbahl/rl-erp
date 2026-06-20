from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    bom_id = Column(Integer, ForeignKey("boms.id"), nullable=False)
    bom_version = Column(Integer, nullable=False)
    quantity_planned = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="DRAFT")
    notes = Column(String, nullable=True)

    status_changed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    product = relationship("Product")
    bom = relationship("BOM")
    items = relationship(
        "ProductionOrderItem",
        back_populates="production_order",
        cascade="all, delete-orphan"
    )
