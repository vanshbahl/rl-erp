from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get("/")
def get_customers():
    return {"message": "Customer route working"}

@router.post("/")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    new_customer = Customer(**customer.model_dump())

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer

