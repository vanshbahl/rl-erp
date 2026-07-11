
## 2026-07-11

Changed:
- Refactored `app/routes/order.py` to move business logic into a dedicated `OrderService` (`app/services/order_service.py`), adopting a cleaner Service Layer architecture.

## 2026-06-21

Added:
- Production Execution manufacturing module:
  - Database models `ProductionExecution` and `ProductionExecutionItem` representing execution headers and component consumption logs.
  - Nullable `production_execution_id` foreign key referencing `production_executions.id` on `inventory_transactions`.
  - API endpoints: POST `/production-orders/{id}/execute` (atomic raw/finished stock mutations, inventory transactions), POST `/production-orders/{id}/rollback` (stock reversal, execution/order state changes), and GET `/production-orders/{id}/executions` (execution audit log).
  - Strict status state machine transition protection in PATCH `/production-orders/{id}/status`.
  - Alembic migration revision `75dbc95f9297` creating tables and updating columns.
- Production Orders planning module:
  - Database models `ProductionOrder` and `ProductionOrderItem` with foreign keys, constraints, and relationships.
  - API endpoints: POST `/production-orders` (scales BOM requirements, prevents self-references), GET `/production-orders` (list headers), GET `/production-orders/{id}` (get details with items), PATCH `/production-orders/{id}/status` (update lifecycle status), and GET `/production-orders/{id}/check-availability` (verify component stock levels).
  - Alembic migration revision `310a4097f923` creating tables `production_orders` and `production_order_items`.

## 2026-06-17

Added:
- Order lifecycle
- Inventory rollback
- Alembic migrations

Changed:
- Replaced Base.metadata.create_all
- Added migration workflow

