from datetime import datetime
from pydantic import BaseModel, Field


class ConsumptionOverride(BaseModel):
    component_product_id: int
    quantity_consumed: float = Field(..., gt=0)


class ProductionExecuteRequest(BaseModel):
    notes: str | None = None
    quantity_produced: float | None = Field(None, gt=0)
    consumption_overrides: list[ConsumptionOverride] | None = None


class ProductionExecutionItemResponse(BaseModel):
    id: int
    execution_id: int
    component_product_id: int
    quantity_required: float
    quantity_consumed: float
    unit_of_measure: str

    class Config:
        from_attributes = True


class ProductionExecutionResponse(BaseModel):
    id: int
    production_order_id: int
    executed_by: int
    quantity_produced: float
    status: str
    notes: str | None
    executed_at: datetime
    rolled_back_at: datetime | None
    items: list[ProductionExecutionItemResponse]

    class Config:
        from_attributes = True
