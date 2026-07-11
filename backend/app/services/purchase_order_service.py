from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.enums import InventoryTransactionType
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction

from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderStatusUpdate,
    PurchaseOrderReceive,
)


class PurchaseOrderService:

    @staticmethod
    def create_purchase_order(db: Session, po_data: PurchaseOrderCreate) -> PurchaseOrder:
        supplier = (
            db.query(Supplier)
            .filter(
                Supplier.id == po_data.supplier_id,
                Supplier.is_active == True
            )
            .first()
        )

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

        from sqlalchemy.exc import IntegrityError

        for attempt in range(3):
            try:
                po_number = PurchaseOrderService._generate_po_number(db)

                purchase_order = PurchaseOrder(
                    supplier_id=po_data.supplier_id,
                    contact_person=po_data.contact_person,
                    po_number=po_number,
                    remarks=po_data.remarks,
                    status="DRAFT",
                    total_amount=0
                )

                db.add(purchase_order)
                db.flush()

                total_amount = 0.0

                for item in po_data.items:
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

                    amount = float(item.quantity) * float(item.rate)

                    po_item = PurchaseOrderItem(
                        purchase_order_id=purchase_order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        rate=item.rate,
                        amount=amount
                    )

                    db.add(po_item)
                    total_amount += amount

                purchase_order.total_amount = total_amount

                db.commit()
                db.refresh(purchase_order)

                return purchase_order
            except IntegrityError:
                db.rollback()
                if attempt == 2:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to generate unique PO number due to high concurrency"
                    )
            except Exception:
                db.rollback()
                raise

    @staticmethod
    def list_purchase_orders(db: Session) -> list[PurchaseOrder]:
        return (
            db.query(PurchaseOrder)
            .order_by(PurchaseOrder.id.desc())
            .all()
        )

    @staticmethod
    def get_purchase_order(db: Session, purchase_order_id: int) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order = (
            db.query(PurchaseOrder)
            .filter(PurchaseOrder.id == purchase_order_id)
            .first()
        )

        if not purchase_order:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found"
            )

        items = (
            db.query(PurchaseOrderItem)
            .filter(PurchaseOrderItem.purchase_order_id == purchase_order.id)
            .all()
        )

        return purchase_order, items
    
    @staticmethod
    def get_items_for_purchase_order(db: Session, purchase_order_id: int) -> list[PurchaseOrderItem]:
        return (
            db.query(PurchaseOrderItem)
            .filter(PurchaseOrderItem.purchase_order_id == purchase_order_id)
            .all()
        )

    @staticmethod
    def transition_status(db: Session, purchase_order_id: int, status_data: PurchaseOrderStatusUpdate) -> PurchaseOrder:
        purchase_order = (
            db.query(PurchaseOrder)
            .filter(PurchaseOrder.id == purchase_order_id)
            .first()
        )

        if not purchase_order:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found"
            )

        PurchaseOrderService._validate_transition(purchase_order.status, status_data.status)

        try:
            purchase_order.status = status_data.status
            db.commit()
            db.refresh(purchase_order)
            return purchase_order
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def receive_goods(db: Session, purchase_order_id: int, receive_data: PurchaseOrderReceive) -> PurchaseOrder:
        purchase_order = (
            db.query(PurchaseOrder)
            .filter(PurchaseOrder.id == purchase_order_id)
            .first()
        )

        if not purchase_order:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found"
            )

        if purchase_order.status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail="Cannot receive a cancelled purchase order"
            )

        po_items = (
            db.query(PurchaseOrderItem)
            .filter(PurchaseOrderItem.purchase_order_id == purchase_order.id)
            .all()
        )

        try:
            PurchaseOrderService._process_receiving(db, purchase_order, po_items, receive_data)
            
            # Check status after processing receipt
            all_received = all(
                item.received_quantity >= item.quantity
                for item in po_items
            )

            any_received = any(
                item.received_quantity > 0
                for item in po_items
            )

            if all_received:
                purchase_order.status = "RECEIVED"
            elif any_received:
                purchase_order.status = "PARTIALLY_RECEIVED"

            db.commit()
            db.refresh(purchase_order)
            return purchase_order
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _validate_transition(current_status: str, new_status: str):
        allowed_transitions = {
            "DRAFT": ["SENT", "CANCELLED"],
            "SENT": ["PARTIALLY_RECEIVED", "RECEIVED", "CANCELLED"],
            "PARTIALLY_RECEIVED": ["RECEIVED", "CANCELLED"],
            "RECEIVED": [],
            "CANCELLED": []
        }

        if current_status not in allowed_transitions:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown current purchase order status: {current_status}"
            )

        if new_status == current_status:
            raise HTTPException(
                status_code=400,
                detail="Purchase order is already in that status"
            )

        if new_status not in allowed_transitions[current_status]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from {current_status} to {new_status}"
            )

    @staticmethod
    def _process_receiving(db: Session, purchase_order: PurchaseOrder, po_items: list[PurchaseOrderItem], receive_data: PurchaseOrderReceive):
        po_item_map = {
            item.product_id: item
            for item in po_items
        }

        for item in receive_data.items:
            if item.product_id not in po_item_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {item.product_id} is not part of this purchase order"
                )

            po_item = po_item_map[item.product_id]

            if item.received_quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Received quantity must be greater than zero"
                )

            remaining_quantity = (
                po_item.quantity - po_item.received_quantity
            )

            if item.received_quantity > remaining_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot receive {item.received_quantity}. "
                        f"Only {remaining_quantity} remaining for product {item.product_id}"
                    )
                )

            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == item.product_id)
                .first()
            )

            if not inventory:
                inventory = Inventory(
                    product_id=item.product_id,
                    quantity=0,
                    minimum_stock=0
                )
                db.add(inventory)
                db.flush()

            inventory.quantity += item.received_quantity
            po_item.received_quantity += item.received_quantity

            transaction = InventoryTransaction(
                product_id=item.product_id,
                purchase_order_id=purchase_order.id,
                quantity_change=item.received_quantity,
                transaction_type=InventoryTransactionType.PURCHASE_RECEIPT.value,
                remarks=f"PO Receipt - {purchase_order.po_number}"
            )

            db.add(transaction)

    @staticmethod
    def _generate_po_number(db: Session) -> str:
        last_po = db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).first()
        if last_po and last_po.po_number and last_po.po_number.startswith("PO-"):
            try:
                last_num = int(last_po.po_number.split("-")[1])
                return f"PO-{(last_num + 1):06d}"
            except (ValueError, IndexError):
                pass
        return "PO-000001"
