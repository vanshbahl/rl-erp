from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(
        Integer,
        ForeignKey("boms.id", ondelete="CASCADE"),
        nullable=False
    )
    component_product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "bom_id",
            "component_product_id",
            name="uq_bom_items_bom_component"
        ),
    )

    bom = relationship("BOM", back_populates="items")
    component = relationship("Product")
