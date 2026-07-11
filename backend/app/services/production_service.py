from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.enums import ProductType, InventoryTransactionType
from app.models.production_order import ProductionOrder
from app.models.production_order_item import ProductionOrderItem
from app.models.product import Product
from app.models.bom import BOM
from app.models.bom_item import BOMItem
from app.models.inventory import Inventory
from app.models.production_execution import ProductionExecution
from app.models.production_execution_item import ProductionExecutionItem
from app.models.inventory_transaction import InventoryTransaction

from app.schemas.production_order import (
    ProductionOrderCreate,
    ProductionOrderStatusUpdate,
)
from app.schemas.production_execution import (
    ProductionExecuteRequest,
)

class ProductionService:

    @staticmethod
    def create_production_order(db: Session, order_data: ProductionOrderCreate) -> ProductionOrder:
        ProductionService._validate_parent_product(db, order_data.product_id)
        active_bom = ProductionService._get_active_bom(db, order_data.product_id)
        
        try:
            db_order = ProductionOrder(
                product_id=order_data.product_id,
                bom_id=active_bom.id,
                bom_version=active_bom.version,
                quantity_planned=order_data.quantity_planned,
                status="DRAFT",
                notes=order_data.notes
            )
            db.add(db_order)
            db.flush()

            ProductionService._snapshot_bom(db, db_order, active_bom, order_data.quantity_planned)

            db.commit()
            db.refresh(db_order)
            return db_order
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def list_production_orders(db: Session) -> list[ProductionOrder]:
        return db.query(ProductionOrder).all()

    @staticmethod
    def get_production_order(db: Session, order_id: int) -> ProductionOrder:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=404,
                detail="Production Order not found"
            )
        return order

    @staticmethod
    def transition_status(db: Session, order_id: int, status_data: ProductionOrderStatusUpdate) -> ProductionOrder:
        order = ProductionService.get_production_order(db, order_id)
        
        ProductionService._validate_transition(order.status, status_data.status.upper())

        try:
            order.status = status_data.status.upper()
            order.status_changed_at = datetime.utcnow()
            db.commit()
            db.refresh(order)
            return order
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def check_availability(db: Session, order_id: int) -> list[dict]:
        order = ProductionService.get_production_order(db, order_id)
        
        report = []
        for item in order.items:
            comp_product = db.query(Product).filter(Product.id == item.component_product_id).first()
            comp_sku = comp_product.sku if comp_product else "UNKNOWN"
            comp_name = comp_product.name if comp_product else "UNKNOWN"

            inventory = db.query(Inventory).filter(Inventory.product_id == item.component_product_id).first()
            available_qty = inventory.quantity if inventory else 0.0

            report.append({
                "component_product_id": item.component_product_id,
                "component_sku": comp_sku,
                "component_name": comp_name,
                "quantity_required": item.quantity_required,
                "quantity_available": available_qty,
                "is_sufficient": available_qty >= item.quantity_required,
                "unit_of_measure": item.unit_of_measure
            })

        return report

    @staticmethod
    def execute_production(db: Session, order_id: int, req_data: ProductionExecuteRequest, current_user_id: int) -> ProductionExecution:
        order = ProductionService.get_production_order(db, order_id)

        if order.status != "IN_PROGRESS":
            raise HTTPException(
                status_code=400,
                detail=f"Production order status must be IN_PROGRESS, but is currently {order.status}"
            )

        existing_completed = db.query(ProductionExecution).filter(
            ProductionExecution.production_order_id == order_id,
            ProductionExecution.status == "COMPLETED"
        ).first()
        if existing_completed:
            raise HTTPException(
                status_code=400,
                detail="A completed execution already exists for this order. Rollback first."
            )

        quantity_produced = req_data.quantity_produced if req_data.quantity_produced is not None else order.quantity_planned
        consumptions = ProductionService._calculate_consumption(db, order, req_data.consumption_overrides)

        try:
            execution = ProductionExecution(
                production_order_id=order.id,
                executed_by=current_user_id,
                quantity_produced=quantity_produced,
                status="COMPLETED",
                notes=req_data.notes,
                executed_at=datetime.utcnow()
            )
            db.add(execution)
            db.flush()

            ProductionService._consume_inventory(db, execution, order, consumptions)
            ProductionService._add_finished_goods(db, execution, order, quantity_produced)

            order.status = "COMPLETED"
            order.status_changed_at = datetime.utcnow()

            db.commit()
            db.refresh(execution)
            return execution
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def rollback_execution(db: Session, order_id: int) -> ProductionExecution:
        order = ProductionService.get_production_order(db, order_id)

        execution = db.query(ProductionExecution).filter(
            ProductionExecution.production_order_id == order_id,
            ProductionExecution.status == "COMPLETED"
        ).order_by(ProductionExecution.executed_at.desc()).first()

        if not execution:
            raise HTTPException(
                status_code=400,
                detail="No completed execution found to roll back."
            )

        output_inventory = db.query(Inventory).filter(Inventory.product_id == order.product_id).first()
        if not output_inventory or output_inventory.quantity < execution.quantity_produced:
            available_qty = output_inventory.quantity if output_inventory else 0.0
            raise HTTPException(
                status_code=400,
                detail=f"Cannot rollback because produced inventory has already been consumed. Required: {execution.quantity_produced}, Available: {available_qty}"
            )

        try:
            ProductionService._rollback_consumption(db, execution)
            ProductionService._rollback_finished_goods(db, execution, order)

            execution.status = "ROLLED_BACK"
            execution.rolled_back_at = datetime.utcnow()

            order.status = "IN_PROGRESS"
            order.status_changed_at = datetime.utcnow()

            db.commit()
            db.refresh(execution)
            return execution
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_executions(db: Session, order_id: int) -> list[ProductionExecution]:
        order = ProductionService.get_production_order(db, order_id)
        
        executions = db.query(ProductionExecution).filter(
            ProductionExecution.production_order_id == order.id
        ).order_by(ProductionExecution.executed_at.desc()).all()

        return executions

    # --- Private Helpers ---

    @staticmethod
    def _validate_parent_product(db: Session, product_id: int):
        parent_product = db.query(Product).filter(Product.id == product_id).first()
        if not parent_product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )
        if parent_product.product_type not in [ProductType.FINISHED_GOOD.value, ProductType.SEMI_FINISHED.value]:
            raise HTTPException(
                status_code=400,
                detail="Production Order product must be FINISHED_GOOD or SEMI_FINISHED"
            )

    @staticmethod
    def _get_active_bom(db: Session, product_id: int) -> BOM:
        active_bom = db.query(BOM).filter(
            BOM.product_id == product_id,
            BOM.is_active == True
        ).first()

        if not active_bom:
            raise HTTPException(
                status_code=400,
                detail=f"No active BOM found for product {product_id}"
            )
        return active_bom

    @staticmethod
    def _snapshot_bom(db: Session, db_order: ProductionOrder, active_bom: BOM, quantity_planned: float):
        bom_items = db.query(BOMItem).filter(BOMItem.bom_id == active_bom.id).all()
        if not bom_items:
            raise HTTPException(
                status_code=400,
                detail=f"BOM {active_bom.id} does not contain any component items"
            )

        allowed_component_types = [
            ProductType.RAW_MATERIAL.value,
            ProductType.SEMI_FINISHED.value,
            ProductType.PACKAGING.value
        ]

        for item in bom_items:
            if item.component_product_id == db_order.product_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Component product {item.component_product_id} cannot reference the parent product (self-reference)"
                )

            comp_product = db.query(Product).filter(Product.id == item.component_product_id).first()
            if not comp_product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Component product {item.component_product_id} not found"
                )
            if comp_product.product_type not in allowed_component_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Component product {item.component_product_id} must be RAW_MATERIAL, SEMI_FINISHED, or PACKAGING"
                )

            quantity_required = item.quantity * quantity_planned

            db_item = ProductionOrderItem(
                production_order_id=db_order.id,
                component_product_id=item.component_product_id,
                quantity_required=quantity_required,
                unit_of_measure=item.unit_of_measure
            )
            db.add(db_item)

    @staticmethod
    def _validate_transition(current_status: str, new_status: str):
        if current_status == "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail="Production order is completed. Use the rollback endpoint to revert."
            )

        if current_status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail="Cancelled orders are terminal and cannot be modified"
            )

        allowed_next_states = {
            "DRAFT": ["PLANNED", "CANCELLED"],
            "PLANNED": ["IN_PROGRESS", "CANCELLED"],
            "IN_PROGRESS": ["CANCELLED"]
        }

        if new_status not in allowed_next_states.get(current_status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Transition from {current_status} to {new_status} is not allowed via status patch. Allowed transitions: {allowed_next_states.get(current_status, [])}"
            )

    @staticmethod
    def _calculate_consumption(db: Session, order: ProductionOrder, consumption_overrides: list) -> list:
        overrides_map = {}
        if consumption_overrides:
            for override in consumption_overrides:
                overrides_map[override.component_product_id] = override.quantity_consumed

        consumptions = []
        insufficient_stock = []

        for item in order.items:
            qty_consumed = overrides_map.get(item.component_product_id, item.quantity_required)

            inventory = db.query(Inventory).filter(Inventory.product_id == item.component_product_id).first()
            if not inventory:
                inventory = Inventory(
                    product_id=item.component_product_id,
                    quantity=0.0,
                    minimum_stock=0.0
                )
                db.add(inventory)
                db.flush()

            if inventory.quantity < qty_consumed:
                insufficient_stock.append({
                    "product_id": item.component_product_id,
                    "required": qty_consumed,
                    "available": inventory.quantity
                })

            consumptions.append((item, qty_consumed, inventory))

        if insufficient_stock:
            details_str = ", ".join([f"Product {x['product_id']} (need {x['required']}, got {x['available']})" for x in insufficient_stock])
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory for components: {details_str}"
            )
            
        return consumptions

    @staticmethod
    def _consume_inventory(db: Session, execution: ProductionExecution, order: ProductionOrder, consumptions: list):
        for item, qty_consumed, inventory in consumptions:
            exec_item = ProductionExecutionItem(
                execution_id=execution.id,
                component_product_id=item.component_product_id,
                quantity_required=item.quantity_required,
                quantity_consumed=qty_consumed,
                unit_of_measure=item.unit_of_measure
            )
            db.add(exec_item)

            inventory.quantity -= qty_consumed

            transaction = InventoryTransaction(
                product_id=item.component_product_id,
                production_execution_id=execution.id,
                quantity_change=-qty_consumed,
                transaction_type=InventoryTransactionType.PRODUCTION_CONSUMPTION.value,
                remarks=f"Execution #{execution.id} - consumed for order #{order.id}"
            )
            db.add(transaction)

    @staticmethod
    def _add_finished_goods(db: Session, execution: ProductionExecution, order: ProductionOrder, quantity_produced: float):
        output_inventory = db.query(Inventory).filter(Inventory.product_id == order.product_id).first()
        if not output_inventory:
            output_inventory = Inventory(
                product_id=order.product_id,
                quantity=0.0,
                minimum_stock=0.0
            )
            db.add(output_inventory)
            db.flush()

        output_inventory.quantity += quantity_produced

        output_transaction = InventoryTransaction(
            product_id=order.product_id,
            production_execution_id=execution.id,
            quantity_change=quantity_produced,
            transaction_type=InventoryTransactionType.PRODUCTION_OUTPUT.value,
            remarks=f"Execution #{execution.id} - produced for order #{order.id}"
        )
        db.add(output_transaction)

    @staticmethod
    def _rollback_consumption(db: Session, execution: ProductionExecution):
        for item in execution.items:
            comp_inventory = db.query(Inventory).filter(Inventory.product_id == item.component_product_id).first()
            if not comp_inventory:
                comp_inventory = Inventory(
                    product_id=item.component_product_id,
                    quantity=0.0,
                    minimum_stock=0.0
                )
                db.add(comp_inventory)
                db.flush()

            comp_inventory.quantity += item.quantity_consumed

            transaction = InventoryTransaction(
                product_id=item.component_product_id,
                production_execution_id=execution.id,
                quantity_change=item.quantity_consumed,
                transaction_type=InventoryTransactionType.REVERSAL.value,
                remarks=f"Rollback of Execution #{execution.id} - restored component"
            )
            db.add(transaction)

    @staticmethod
    def _rollback_finished_goods(db: Session, execution: ProductionExecution, order: ProductionOrder):
        output_inventory = db.query(Inventory).filter(Inventory.product_id == order.product_id).first()
        output_inventory.quantity -= execution.quantity_produced

        output_transaction = InventoryTransaction(
            product_id=order.product_id,
            production_execution_id=execution.id,
            quantity_change=-execution.quantity_produced,
            transaction_type=InventoryTransactionType.REVERSAL.value,
            remarks=f"Rollback of Execution #{execution.id} - removed output"
        )
        db.add(output_transaction)
