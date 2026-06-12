from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get("/")
def get_customers(
    db: Session = Depends(get_db)
):
    customers = db.query(Customer).all()
    return customers

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

@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        return {"error": "Customer not found"}

    return customer

@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        return {"error": "Customer not found"}

    for key, value in customer_data.model_dump().items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        return {"error": "Customer not found"}

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted"}