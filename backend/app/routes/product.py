from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.schemas.product import ProductCreate, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/")
def get_products(
    db: Session = Depends(get_db)
):
    return db.query(Product).all()

@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@router.get("/")
def get_products(
    db: Session = Depends(get_db)
):
    return db.query(Product).all()

@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return {"error": "Product not found"}

    return product

@router.put("/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return {"error": "Product not found"}

    for key, value in product_data.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return {"error": "Product not found"}

    db.delete(product)
    db.commit()

    return {"message": "Product deleted"}