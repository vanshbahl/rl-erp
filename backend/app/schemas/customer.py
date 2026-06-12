from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    company_name: str
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    gst_number: str | None = None

class CustomerResponse(CustomerCreate):
    id: int

    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    company_name: str
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    gst_number: str | None = None