from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float

    payment_method: str

    reference_number: Optional[str] = None
    remarks: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int

    invoice_id: int
    amount: float

    payment_method: str

    reference_number: Optional[str]
    remarks: Optional[str]

    payment_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True