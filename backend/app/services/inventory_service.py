from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryService:

    @staticmethod
    def get_inventory(db: Session) -> list[Inventory]:
        return db.query(Inventory).all()

    @staticmethod
    def get_low_stock(db: Session, product_type: str | None = None, supplier_id: int | None = None) -> list[Inventory]:
        query = db.query(Inventory).join(Product, Inventory.product_id == Product.id)
        
        query = query.filter(Inventory.quantity <= Inventory.minimum_stock)
        
        if product_type:
            query = query.filter(Product.product_type == product_type)
            
        if supplier_id:
            query = query.filter(Product.default_supplier_id == supplier_id)
            
        return query.all()

    @staticmethod
    def get_inventory_item(db: Session, product_id: int) -> Inventory:
        inventory = (
            db.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .first()
        )

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail="Inventory record not found"
            )

        return inventory

    @staticmethod
    def create_inventory(db: Session, inventory: InventoryCreate) -> Inventory:
        try:
            existing = (
                db.query(Inventory)
                .filter(Inventory.product_id == inventory.product_id)
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Inventory record already exists"
                )

            new_inventory = Inventory(**inventory.model_dump())

            db.add(new_inventory)
            db.commit()
            db.refresh(new_inventory)

            return new_inventory
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def update_inventory(db: Session, product_id: int, inventory_data: InventoryUpdate) -> Inventory:
        try:
            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == product_id)
                .first()
            )

            if not inventory:
                raise HTTPException(
                    status_code=404,
                    detail="Inventory record not found"
                )

            for key, value in inventory_data.model_dump(exclude_unset=True).items():
                setattr(inventory, key, value)

            db.commit()
            db.refresh(inventory)

            return inventory
        except Exception:
            db.rollback()
            raise
