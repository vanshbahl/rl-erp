from datetime import datetime

from pydantic import BaseModel

from app.models.order_status import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    rate: float


class OrderCreate(BaseModel):
    customer_id: int
    contact_person: str
    po_number: str | None = None
    remarks: str | None = None

    items: list[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    contact_person: str
    po_number: str | None = None
    status: str
    remarks: str | None = None
    total_amount: float
    order_date: datetime

    class Config:
        from_attributes = True