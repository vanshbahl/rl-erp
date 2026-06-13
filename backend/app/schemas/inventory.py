

from pydantic import BaseModel


class InventoryCreate(BaseModel):
    product_id: int
    quantity: float = 0
    minimum_stock: float = 0


class InventoryUpdate(BaseModel):
    quantity: float | None = None
    minimum_stock: float | None = None


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    minimum_stock: float

    class Config:
        from_attributes = True