from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_roles, get_current_user
from app.models.enums import UserRole
from app.models.user import User

from app.schemas.production_order import (
    ProductionOrderCreate,
    ProductionOrderResponse,
    ProductionOrderStatusUpdate
)
from app.schemas.production_execution import (
    ProductionExecuteRequest,
    ProductionExecutionResponse
)

from app.services.production_service import ProductionService

router = APIRouter(
    prefix="/production-orders",
    tags=["Production"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGER
            )
        )
    ]
)

@router.post(
    "",
    response_model=ProductionOrderResponse
)
def create_production_order(
    order_data: ProductionOrderCreate,
    db: Session = Depends(get_db)
):
    order = ProductionService.create_production_order(db, order_data)
    return order


@router.get(
    "",
    response_model=list[ProductionOrderResponse]
)
def get_production_orders(
    db: Session = Depends(get_db)
):
    return ProductionService.list_production_orders(db)


@router.get(
    "/{order_id}",
    response_model=ProductionOrderResponse
)
def get_production_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    return ProductionService.get_production_order(db, order_id)


@router.patch(
    "/{order_id}/status",
    response_model=ProductionOrderResponse
)
def update_production_order_status(
    order_id: int,
    status_data: ProductionOrderStatusUpdate,
    db: Session = Depends(get_db)
):
    return ProductionService.transition_status(db, order_id, status_data)


@router.get(
    "/{order_id}/availability",
    response_model=list[dict]
)
def check_production_order_availability(
    order_id: int,
    db: Session = Depends(get_db)
):
    return ProductionService.check_availability(db, order_id)


@router.post(
    "/{order_id}/execute",
    response_model=ProductionExecutionResponse
)
def execute_production_order(
    order_id: int,
    req_data: ProductionExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProductionService.execute_production(db, order_id, req_data, current_user.id)


@router.post(
    "/{order_id}/rollback",
    response_model=ProductionExecutionResponse
)
def rollback_production_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    return ProductionService.rollback_execution(db, order_id)


@router.get(
    "/{order_id}/executions",
    response_model=list[ProductionExecutionResponse]
)
def get_production_executions(
    order_id: int,
    db: Session = Depends(get_db)
):
    return ProductionService.get_executions(db, order_id)
