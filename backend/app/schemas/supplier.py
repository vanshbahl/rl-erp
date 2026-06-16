from pydantic import BaseModel, EmailStr


class SupplierCreate(BaseModel):
    company_name: str
    contact_person: str | None = None

    phone: str | None = None
    email: EmailStr | None = None

    gst_number: str | None = None

    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None


class SupplierResponse(SupplierCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class SupplierUpdate(BaseModel):
    company_name: str | None = None
    contact_person: str | None = None

    phone: str | None = None
    email: EmailStr | None = None

    gst_number: str | None = None

    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None