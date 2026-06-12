from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    sku: str

    hsn_code: str | None = None
    gst_rate: int | None = None

    unit: str | None = None
    base_price: int | None = None

    color: str | None = None
    description: str | None = None


class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True

class ProductUpdate(ProductCreate):
    pass