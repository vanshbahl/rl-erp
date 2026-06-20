from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole, ProductType, InventoryTransactionType
from app.models.user import User
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
    ProductionOrderResponse
)
from app.schemas.production_execution import (
    ProductionExecuteRequest,
    ProductionExecutionResponse
)

router = APIRouter(
    prefix="/production-orders",
    tags=["Production Orders"]
)


@router.post("", response_model=ProductionOrderResponse)
def create_production_order(
    order_data: ProductionOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    # 1. Validate parent product exists and is type FINISHED_GOOD or SEMI_FINISHED
    parent_product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not parent_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product {order_data.product_id} not found"
        )
    if parent_product.product_type not in [ProductType.FINISHED_GOOD.value, ProductType.SEMI_FINISHED.value]:
        raise HTTPException(
            status_code=400,
            detail="Production Order product must be FINISHED_GOOD or SEMI_FINISHED"
        )

    # 2. Retrieve active BOM for the product
    active_bom = db.query(BOM).filter(
        BOM.product_id == order_data.product_id,
        BOM.is_active == True
    ).first()

    if not active_bom:
        raise HTTPException(
            status_code=400,
            detail=f"No active BOM found for product {order_data.product_id}"
        )

    # 3. Create the Production Order header
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

    # 4. Fetch BOM components and validate
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
        # Prevent direct self-reference
        if item.component_product_id == order_data.product_id:
            raise HTTPException(
                status_code=400,
                detail=f"Component product {item.component_product_id} cannot reference the parent product (self-reference)"
            )

        # Check component product type
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

        # Calculate required quantity: scaled directly
        quantity_required = item.quantity * order_data.quantity_planned

        db_item = ProductionOrderItem(
            production_order_id=db_order.id,
            component_product_id=item.component_product_id,
            quantity_required=quantity_required,
            unit_of_measure=item.unit_of_measure
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("", response_model=list[ProductionOrderResponse])
def get_production_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    return db.query(ProductionOrder).all()


@router.get("/{id}", response_model=ProductionOrderResponse)
def get_production_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Production Order not found"
        )
    return order


@router.patch("/{id}/status", response_model=ProductionOrderResponse)
def update_production_order_status(
    id: int,
    status_data: ProductionOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Production Order not found"
        )

    current_status = order.status
    new_status = status_data.status.upper()

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

    order.status = new_status
    order.status_changed_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


@router.get("/{id}/check-availability")
def check_production_order_availability(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Production Order not found"
        )

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


@router.post("/{id}/execute", response_model=ProductionExecutionResponse)
def execute_production_order(
    id: int,
    req_data: ProductionExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    # 1. Fetch Production Order
    order = db.query(ProductionOrder).filter(ProductionOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Production Order not found"
        )

    # 2. Verify status is IN_PROGRESS
    if order.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail=f"Production order status must be IN_PROGRESS, but is currently {order.status}"
        )

    # 3. Check for existing COMPLETED execution
    existing_completed = db.query(ProductionExecution).filter(
        ProductionExecution.production_order_id == id,
        ProductionExecution.status == "COMPLETED"
    ).first()
    if existing_completed:
        raise HTTPException(
            status_code=400,
            detail="A completed execution already exists for this order. Rollback first."
        )

    # 4. Fetch overrides and default values
    overrides_map = {}
    if req_data.consumption_overrides:
        for override in req_data.consumption_overrides:
            overrides_map[override.component_product_id] = override.quantity_consumed

    # Calculate actual consumption per item and validate stock availability
    consumptions = []
    insufficient_stock = []

    for item in order.items:
        qty_consumed = overrides_map.get(item.component_product_id, item.quantity_required)

        # Verify component inventory record exists
        inventory = db.query(Inventory).filter(Inventory.product_id == item.component_product_id).first()
        if not inventory:
            # Create inventory row with quantity=0
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

    # Determine quantity produced
    quantity_produced = req_data.quantity_produced if req_data.quantity_produced is not None else order.quantity_planned

    # Verify/create finished good output inventory row
    output_inventory = db.query(Inventory).filter(Inventory.product_id == order.product_id).first()
    if not output_inventory:
        output_inventory = Inventory(
            product_id=order.product_id,
            quantity=0.0,
            minimum_stock=0.0
        )
        db.add(output_inventory)
        db.flush()

    try:
        # Create ProductionExecution
        execution = ProductionExecution(
            production_order_id=order.id,
            executed_by=current_user.id,
            quantity_produced=quantity_produced,
            status="COMPLETED",
            notes=req_data.notes,
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.flush()

        # Deduct consumed components and create execution items
        for item, qty_consumed, inventory in consumptions:
            # Create ProductionExecutionItem
            exec_item = ProductionExecutionItem(
                execution_id=execution.id,
                component_product_id=item.component_product_id,
                quantity_required=item.quantity_required,
                quantity_consumed=qty_consumed,
                unit_of_measure=item.unit_of_measure
            )
            db.add(exec_item)

            # Deduct inventory
            inventory.quantity -= qty_consumed

            # Create inventory transaction
            transaction = InventoryTransaction(
                product_id=item.component_product_id,
                production_execution_id=execution.id,
                quantity_change=-qty_consumed,
                transaction_type=InventoryTransactionType.PRODUCTION_CONSUMPTION.value,
                remarks=f"Execution #{execution.id} - consumed for order #{order.id}"
            )
            db.add(transaction)

        # Add produced finished good to inventory
        output_inventory.quantity += quantity_produced

        # Create output inventory transaction
        output_transaction = InventoryTransaction(
            product_id=order.product_id,
            production_execution_id=execution.id,
            quantity_change=quantity_produced,
            transaction_type=InventoryTransactionType.PRODUCTION_OUTPUT.value,
            remarks=f"Execution #{execution.id} - produced for order #{order.id}"
        )
        db.add(output_transaction)

        # Transition production order status to COMPLETED
        order.status = "COMPLETED"
        order.status_changed_at = datetime.utcnow()

        db.commit()
        db.refresh(execution)
        return execution

    except Exception:
        db.rollback()
        raise


@router.post("/{id}/rollback", response_model=ProductionExecutionResponse)
def rollback_production_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):
    # 1. Fetch Production Order
    order = db.query(ProductionOrder).filter(ProductionOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Production Order not found"
        )

    # 2. Locate completed execution
    execution = db.query(ProductionExecution).filter(
        ProductionExecution.production_order_id == id,
        ProductionExecution.status == "COMPLETED"
    ).order_by(ProductionExecution.executed_at.desc()).first()

    if not execution:
        raise HTTPException(
            status_code=400,
            detail="No completed execution found to roll back."
        )

    # 3. Before rollback, verify output inventory
    output_inventory = db.query(Inventory).filter(Inventory.product_id == order.product_id).first()
    if not output_inventory or output_inventory.quantity < execution.quantity_produced:
        available_qty = output_inventory.quantity if output_inventory else 0.0
        raise HTTPException(
            status_code=400,
            detail=f"Cannot rollback because produced inventory has already been consumed. Required: {execution.quantity_produced}, Available: {available_qty}"
        )

    try:
        # Revert component deductions
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

            # Create reversal transaction
            transaction = InventoryTransaction(
                product_id=item.component_product_id,
                production_execution_id=execution.id,
                quantity_change=item.quantity_consumed,
                transaction_type=InventoryTransactionType.REVERSAL.value,
                remarks=f"Rollback of Execution #{execution.id} - restored component"
            )
            db.add(transaction)

        # Revert output finished goods additions
        output_inventory.quantity -= execution.quantity_produced

        output_transaction = InventoryTransaction(
            product_id=order.product_id,
            production_execution_id=execution.id,
            quantity_change=-execution.quantity_produced,
            transaction_type=InventoryTransactionType.REVERSAL.value,
            remarks=f"Rollback of Execution #{execution.id} - removed output"
        )
        db.add(output_transaction)

        # Mark execution as ROLLED_BACK
        execution.status = "ROLLED_BACK"
        execution.rolled_back_at = datetime.utcnow()

        # Transition production order status back to IN_PROGRESS
        order.status = "IN_PROGRESS"
        order.status_changed_at = datetime.utcnow()

        db.commit()
        db.refresh(execution)
        return execution

    except Exception:
        db.rollback()
        raise


@router.get("/{id}/executions", response_model=list[ProductionExecutionResponse])
def get_production_order_executions(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.STAFF
        )
    )
):
    # 1. Fetch Production Order to verify existence
    order = db.query(ProductionOrder).filter(ProductionOrder.id == id).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Production Order not found"
        )

    # 2. Get execution history sorted by executed_at DESC
    executions = db.query(ProductionExecution).filter(
        ProductionExecution.production_order_id == id
    ).order_by(ProductionExecution.executed_at.desc()).all()

    return executions
