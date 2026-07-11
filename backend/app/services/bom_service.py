from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.enums import ProductType
from app.models.bom import BOM
from app.models.bom_item import BOMItem
from app.models.product import Product
from app.schemas.bom import BOMCreate, BOMUpdate


class BOMService:

    @staticmethod
    def create_bom(db: Session, bom_data: BOMCreate) -> BOM:
        try:
            BOMService._validate_bom_constraints(db, bom_data.product_id, bom_data.items)

            if bom_data.is_active:
                BOMService._handle_active_bom_deactivation(db, bom_data.product_id)

            db_bom = BOM(
                product_id=bom_data.product_id,
                version=bom_data.version,
                is_active=bom_data.is_active,
                notes=bom_data.notes
            )
            db.add(db_bom)
            db.flush()

            for item in bom_data.items:
                db_item = BOMItem(
                    bom_id=db_bom.id,
                    component_product_id=item.component_product_id,
                    quantity=item.quantity,
                    unit_of_measure=item.unit_of_measure
                )
                db.add(db_item)

            db.commit()
            db.refresh(db_bom)
            return db_bom
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def list_boms(db: Session) -> list[BOM]:
        return db.query(BOM).all()

    @staticmethod
    def get_active_bom_by_product(db: Session, product_id: int) -> BOM:
        bom = db.query(BOM).filter(
            BOM.product_id == product_id,
            BOM.is_active == True
        ).first()

        if not bom:
            raise HTTPException(
                status_code=404,
                detail=f"No active BOM found for product {product_id}"
            )
        return bom

    @staticmethod
    def get_bom(db: Session, id: int) -> BOM:
        bom = db.query(BOM).filter(BOM.id == id).first()
        if not bom:
            raise HTTPException(
                status_code=404,
                detail="BOM not found"
            )
        return bom

    @staticmethod
    def update_bom(db: Session, id: int, bom_data: BOMUpdate) -> BOM:
        try:
            bom = db.query(BOM).filter(BOM.id == id).first()
            if not bom:
                raise HTTPException(
                    status_code=404,
                    detail="BOM not found"
                )

            if bom_data.version is not None:
                bom.version = bom_data.version

            if bom_data.notes is not None:
                bom.notes = bom_data.notes

            if bom_data.is_active is not None:
                if bom_data.is_active and not bom.is_active:
                    BOMService._handle_active_bom_deactivation(db, bom.product_id, exclude_bom_id=bom.id)
                bom.is_active = bom_data.is_active

            if bom_data.items is not None:
                BOMService._validate_bom_constraints(db, bom.product_id, bom_data.items)
                db.query(BOMItem).filter(BOMItem.bom_id == bom.id).delete()
                for item in bom_data.items:
                    db_item = BOMItem(
                        bom_id=bom.id,
                        component_product_id=item.component_product_id,
                        quantity=item.quantity,
                        unit_of_measure=item.unit_of_measure
                    )
                    db.add(db_item)

            db.commit()
            db.refresh(bom)
            return bom
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def activate_bom(db: Session, id: int) -> BOM:
        try:
            bom = db.query(BOM).filter(BOM.id == id).first()
            if not bom:
                raise HTTPException(
                    status_code=404,
                    detail="BOM not found"
                )

            if not bom.is_active:
                BOMService._handle_active_bom_deactivation(db, bom.product_id, exclude_bom_id=bom.id)
                bom.is_active = True
                db.commit()
                db.refresh(bom)

            return bom
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _validate_bom_constraints(db: Session, parent_product_id: int, items: list) -> None:
        parent_product = db.query(Product).filter(Product.id == parent_product_id).first()
        if not parent_product:
            raise HTTPException(
                status_code=404,
                detail=f"Parent product {parent_product_id} not found"
            )
        if parent_product.product_type not in [ProductType.FINISHED_GOOD.value, ProductType.SEMI_FINISHED.value]:
            raise HTTPException(
                status_code=400,
                detail="BOM parent product must be FINISHED_GOOD or SEMI_FINISHED"
            )

        component_ids = [item.component_product_id for item in items]
        if len(component_ids) != len(set(component_ids)):
            raise HTTPException(
                status_code=400,
                detail="Duplicate component product IDs are not allowed in the same BOM"
            )

        allowed_component_types = [
            ProductType.RAW_MATERIAL.value,
            ProductType.SEMI_FINISHED.value,
            ProductType.PACKAGING.value
        ]

        for item in items:
            if item.component_product_id == parent_product_id:
                raise HTTPException(
                    status_code=400,
                    detail="Component product ID cannot be the same as the parent product ID (self-reference)"
                )

            component_product = db.query(Product).filter(Product.id == item.component_product_id).first()
            if not component_product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Component product {item.component_product_id} not found"
                )
            if component_product.product_type not in allowed_component_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Component product {item.component_product_id} must be RAW_MATERIAL, SEMI_FINISHED, or PACKAGING"
                )

    @staticmethod
    def _handle_active_bom_deactivation(db: Session, product_id: int, exclude_bom_id: int | None = None) -> None:
        query = db.query(BOM).filter(
            BOM.product_id == product_id,
            BOM.is_active == True
        )
        if exclude_bom_id:
            query = query.filter(BOM.id != exclude_bom_id)
            
        active_boms = query.all()
        for bom in active_boms:
            bom.is_active = False
