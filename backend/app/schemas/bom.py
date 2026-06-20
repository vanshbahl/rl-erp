from datetime import datetime
from pydantic import BaseModel, Field


class BOMItemBase(BaseModel):
    component_product_id: int
    quantity: float = Field(..., gt=0)
    unit_of_measure: str = Field(..., min_length=1)


class BOMItemCreate(BOMItemBase):
    pass


class BOMItemResponse(BOMItemBase):
    id: int
    bom_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BOMBase(BaseModel):
    product_id: int
    version: int = Field(default=1, ge=1)
    is_active: bool = True
    notes: str | None = None


class BOMCreate(BOMBase):
    items: list[BOMItemCreate] = Field(..., min_length=1)


class BOMUpdate(BaseModel):
    version: int | None = Field(default=None, ge=1)
    is_active: bool | None = None
    notes: str | None = None
    items: list[BOMItemCreate] | None = None


class BOMResponse(BOMBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: list[BOMItemResponse]

    class Config:
        from_attributes = True
