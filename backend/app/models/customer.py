from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    gst_number = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)