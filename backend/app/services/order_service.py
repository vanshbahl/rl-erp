from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.schemas.order import OrderCreate, OrderStatusUpdate


class OrderService:

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> Order:
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

        try:
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
            return order
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def list_orders(db: Session) -> list[Order]:
        return db.query(Order).all()

    @staticmethod
    def get_order(db: Session, order_id: int) -> tuple[Order, list[OrderItem]]:
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

        return order, items

    @staticmethod
    def transition_status(db: Session, order_id: int, status_data: OrderStatusUpdate) -> Order:
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

        OrderService._validate_transition(order, status_data)

        try:
            previous_status = order.status
            new_status = status_data.status.value

            if new_status == "DISPATCHED" and previous_status != "DISPATCHED":
                OrderService._dispatch_order(db, order)
            elif new_status == "CANCELLED" and previous_status == "DISPATCHED":
                OrderService._cancel_order(db, order)

            order.status = new_status
            db.commit()
            db.refresh(order)
            return order

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _validate_transition(order: Order, status_data: OrderStatusUpdate):
        allowed_transitions = {
            "PENDING": ["PROCESSING", "CANCELLED"],
            "PROCESSING": ["DISPATCHED", "CANCELLED"],
            "DISPATCHED": ["COMPLETED", "CANCELLED"],
            "COMPLETED": [],
            "CANCELLED": [],
        }

        current = order.status
        new = status_data.status.value

        if current not in allowed_transitions:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown current order status: {current}"
            )

        if new == current:
            raise HTTPException(
                status_code=400,
                detail="Order is already in that status"
            )

        if new not in allowed_transitions[current]:
            raise HTTPException(
                status_code=400,
                detail=f"Transition from {current} to {new} is not allowed. Allowed: {allowed_transitions[current]}"
            )

    @staticmethod
    def _dispatch_order(db: Session, order: Order):
        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        # First validate stock availability
        for item in order_items:
            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == item.product_id)
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

        # Then deduct stock and log transactions
        for item in order_items:
            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == item.product_id)
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

    @staticmethod
    def _cancel_order(db: Session, order: Order):
        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        for item in order_items:
            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == item.product_id)
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
