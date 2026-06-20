from sqlalchemy import Column, Integer, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductionExecutionItem(Base):
    __tablename__ = "production_execution_items"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(
        Integer,
        ForeignKey("production_executions.id", ondelete="CASCADE"),
        nullable=False
    )
    component_product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    quantity_required = Column(Float, nullable=False)
    quantity_consumed = Column(Float, nullable=False)
    unit_of_measure = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "execution_id",
            "component_product_id",
            name="uq_exec_items_exec_component"
        ),
    )

    execution = relationship("ProductionExecution", back_populates="items")
    component = relationship("Product")
