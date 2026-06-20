from datetime import datetime
from pydantic import BaseModel, Field


class ProductionOrderItemResponse(BaseModel):
    id: int
    production_order_id: int
    component_product_id: int
    quantity_required: float
    unit_of_measure: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProductionOrderCreate(BaseModel):
    product_id: int
    quantity_planned: float = Field(..., gt=0)
    notes: str | None = None


class ProductionOrderStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1)


class ProductionOrderResponse(BaseModel):
    id: int
    product_id: int
    bom_id: int
    bom_version: int
    quantity_planned: float
    status: str
    notes: str | None
    status_changed_at: datetime
    created_at: datetime
    updated_at: datetime
    items: list[ProductionOrderItemResponse]

    class Config:
        from_attributes = True
