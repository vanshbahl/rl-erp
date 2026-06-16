from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.dependencies.auth import require_roles
from app.models.enums import UserRole

from app.models.supplier import Supplier

from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGER,
            )
        )
    ]
)


@router.post(
    "",
    response_model=SupplierResponse
)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db)
):

    supplier = Supplier(
        company_name=supplier_data.company_name,
        contact_person=supplier_data.contact_person,
        phone=supplier_data.phone,
        email=supplier_data.email,
        gst_number=supplier_data.gst_number,
        address=supplier_data.address,
        city=supplier_data.city,
        state=supplier_data.state,
        pincode=supplier_data.pincode,
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


@router.get(
    "",
    response_model=list[SupplierResponse]
)
def get_suppliers(
    db: Session = Depends(get_db)
):

    return (
        db.query(Supplier)
        .filter(Supplier.is_active == True)
        .all()
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id,
            Supplier.is_active == True
        )
        .first()
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return supplier


@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):

    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id,
            Supplier.is_active == True
        )
        .first()
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    update_data = supplier_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            supplier,
            field,
            value
        )

    db.commit()
    db.refresh(supplier)

    return supplier


@router.delete(
    "/{supplier_id}"
)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):

    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id,
            Supplier.is_active == True
        )
        .first()
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    supplier.is_active = False

    db.commit()

    return {
        "message": "Supplier deactivated successfully"
    }