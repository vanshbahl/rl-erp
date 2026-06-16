from pydantic import BaseModel
from typing import List


class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    rate: float


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    contact_person: str | None = None
    remarks: str | None = None

    items: List[PurchaseOrderItemCreate]


class PurchaseOrderItemResponse(BaseModel):
    id: int

    product_id: int
    quantity: float
    rate: float
    amount: float

    class Config:
        from_attributes = True


class PurchaseOrderResponse(BaseModel):
    id: int

    supplier_id: int

    contact_person: str | None
    po_number: str | None

    status: str

    remarks: str | None

    total_amount: float

    items: List[PurchaseOrderItemResponse]

    class Config:
        from_attributes = True


class PurchaseOrderStatusUpdate(BaseModel):
    status: str