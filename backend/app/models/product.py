from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy import Float


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