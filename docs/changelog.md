
## 2026-07-11 — v1.0 Stabilization Pass

Fixed:
- `OrderService._validate_transition()`: Replaced permissive guard with strict allowlist state machine. Prevents `PENDING → COMPLETED`, re-dispatch, and all backward/skipped transitions. Resolves inventory double-deduction and missing-deduction corruption paths.
- `routes/product.py` `create_product`: Wrapped product creation and initial inventory record creation in a single atomic transaction. Prevents orphaned product records with no inventory row.
- `PurchaseOrderService.create_purchase_order()`: Replaced `COUNT(*)+1` PO number generation with max-ID based strategy and `IntegrityError` retry loop, matching `InvoiceService` pattern.
- `routes/invoice.py`: Added `require_roles(ADMIN, MANAGER, STAFF)` authentication to `GET /invoices` and `GET /invoices/{invoice_id}`.
- `core/security.py`: Removed dead hardcoded `SECRET_KEY = "your-secret-key"` and `ALGORITHM = "HS256"` assignments that were silently overwritten.
- `core/config.py`: Application now fails at startup with a `ValueError` if `SECRET_KEY` environment variable is not set.

## 2026-07-11

Changed:
- Refactored `app/routes/order.py` to move business logic into a dedicated `OrderService` (`app/services/order_service.py`), adopting a cleaner Service Layer architecture.
- Refactored `app/routes/purchase_order.py` to move business logic into a dedicated `PurchaseOrderService` (`app/services/purchase_order_service.py`), further adopting the Service Layer architecture.
- Refactored `app/routes/invoice.py` to move business logic into a dedicated `InvoiceService` (`app/services/invoice_service.py`).
- Refactored `app/routes/payment.py` to move business logic into a dedicated `PaymentService` (`app/services/payment_service.py`).
- Refactored `app/routes/production_order.py` to move business logic into a dedicated `ProductionService` (`app/services/production_service.py`).
- Refactored `app/routes/bom.py` to move business logic into a dedicated `BOMService` (`app/services/bom_service.py`).
- Refactored `app/routes/inventory.py` to move business logic into a dedicated `InventoryService` (`app/services/inventory_service.py`).

Fixed:
- Added transaction guard to `OrderService.create_order` to prevent unhandled dirty sessions.
- Added `PARTIALLY_PAID` status to `InvoiceService` state machine.
- Fixed missing status validation in `routes/payment.py` that allowed payments against DRAFT/CANCELLED invoices.
- Fixed race condition in `InvoiceService.generate_invoice` numbering by implementing a concurrency-safe `IntegrityError` retry loop instead of `COUNT()`.

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

