from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from app.core.database import Base
from sqlalchemy import Float
from app.models.enums import ProductType


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)

    hsn_code = Column(String)
    gst_rate = Column(Integer)
    base_price = Column(Float)

    color = Column(String)
    unit = Column(String)
    description = Column(String)
    product_type = Column(
        String,
        default=ProductType.FINISHED_GOOD.value,
        nullable=False
    )
    standard_cost = Column(Numeric(14, 2), default=0.00, nullable=False)
    default_supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)