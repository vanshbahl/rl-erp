from datetime import datetime

from pydantic import BaseModel


class InvoiceStatusUpdate(BaseModel):
    status: str


class InvoiceItemResponse(BaseModel):
    product_id: int
    quantity: float
    rate: float
    amount: float

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    order_id: int
    customer_id: int

    subtotal: float
    tax_amount: float
    total_amount: float

    status: str
    created_at: datetime

    class Config:
        from_attributes = True