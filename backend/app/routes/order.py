from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.order import (
    OrderCreate,
    OrderStatusUpdate
)

from app.core.database import get_db
from app.dependencies.auth import require_roles

from app.models.enums import UserRole
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction

from app.models.order_status import OrderStatus


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == order_data.customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    order = Order(
        customer_id=order_data.customer_id,
        contact_person=order_data.contact_person,
        po_number=order_data.po_number,
        remarks=order_data.remarks
    )

    db.add(order)
    db.flush()

    order_total = 0.0

    for item in order_data.items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        amount = item.quantity * item.rate
        order_total += amount

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            rate=item.rate,
            amount=amount
        )

        db.add(order_item)


    order.total_amount = order_total

    db.commit()
    db.refresh(order)

    return {
        "message": "Order created successfully",
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
    }


@router.get("/")
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return db.query(Order).all()


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .all()
    )

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": items
    }


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    previous_status = order.status

    if (
        order.status == "COMPLETED"
        and status_data.status.value != "COMPLETED"
    ):
        raise HTTPException(
            status_code=400,
            detail="Completed orders cannot be modified"
        )

    try:

        if (
            status_data.status.value == "DISPATCHED"
            and previous_status != "DISPATCHED"
        ):

            order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.id)
                .all()
            )

            for item in order_items:

                inventory = (
                    db.query(Inventory)
                    .filter(
                        Inventory.product_id == item.product_id
                    )
                    .first()
                )

                if not inventory:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Inventory not found for product {item.product_id}"
                    )

                if inventory.quantity < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient inventory for product {item.product_id}"
                    )

            for item in order_items:

                inventory = (
                    db.query(Inventory)
                    .filter(
                        Inventory.product_id == item.product_id
                    )
                    .first()
                )

                inventory.quantity -= item.quantity

                db.add(
                    InventoryTransaction(
                        product_id=item.product_id,
                        order_id=order.id,
                        quantity_change=-item.quantity,
                        transaction_type="ORDER_DISPATCH",
                        remarks=f"Order #{order.id} dispatched"
                    )
                )

        elif (
            status_data.status.value == "CANCELLED"
            and previous_status == "DISPATCHED"
        ):

            order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.id)
                .all()
            )

            for item in order_items:

                inventory = (
                    db.query(Inventory)
                    .filter(
                        Inventory.product_id == item.product_id
                    )
                    .first()
                )

                if not inventory:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Inventory not found for product {item.product_id}"
                    )

                inventory.quantity += item.quantity

                db.add(
                    InventoryTransaction(
                        product_id=item.product_id,
                        order_id=order.id,
                        quantity_change=item.quantity,
                        transaction_type="ORDER_CANCEL",
                        remarks=f"Order #{order.id} cancelled"
                    )
                )

        order.status = status_data.status.value

        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Order status updated",
        "order_id": order.id,
        "status": order.status
    }