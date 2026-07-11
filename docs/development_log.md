# Development Log - RL-ERP

## 2026-06-21: Production Orders Integration

### Context
Implemented the planning and scheduling portion of the Production module, introducing the ability to organize production runs, scale BOM component requirements, and verify component availability from inventory.

### Key Engineering Decisions
1. **Separation of Planning and Execution**:
   * *Decision*: Restrict the current implementation to planning ONLY. No database mutations to stock (no reservations, no stock consumption, no finished goods yield additions) are performed in this phase.
   * *Rationale*: Keeps schema and database operations minimal, preventing side-effects on inventory until the core planning layer is thoroughly tested.
2. **BOM Version Snapshotting**:
   * *Decision*: The production order header records `bom_id` and `bom_version` explicitly. It scales the required component quantities and copies them into a static `production_order_items` snapshot table.
   * *Tradeoff*: Duplicates recipe details. However, it ensures that subsequent changes or version bumps to a Bill of Materials will not historically alter previously generated production order component lists.
3. **Scaled Quantity Calculation**:
   * *Decision*: Component required quantities scale directly: `quantity_required = bom_item.quantity * production_order.quantity_planned`.
   * *Tradeoff*: Assumes linear scaling of ingredients. Non-linear scaling or batch-fixed additions are deferred to future production iterations.
4. **Unique Component Constraint**:
   * *Decision*: A database-level unique constraint is added to `production_order_items` on `(production_order_id, component_product_id)`.
   * *Rationale*: Prevents multiple redundant rows for the same raw material component within a single production run.

### Database Changes
* Created `production_orders` (Header) table.
* Created `production_order_items` (Component snapshotted details) table with a Cascade Delete foreign key on the production order ID and a composite Unique Constraint.
* Applied via Alembic migration revision `310a4097f923`.

### API Routes
* `POST /production-orders` - Registers a production order, checks BOM existence, verifies parent/component product type classifications, checks self-reference, scales item quantities, and creates snapshots.
* `GET /production-orders` - Lists scheduled orders.
* `GET /production-orders/{id}` - Retrieves detailed scheduled order.
* `PATCH /production-orders/{id}/status` - Status transitions (`DRAFT`, `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).
* `GET /production-orders/{id}/check-availability` - Compares required items vs. active inventory levels.

## 2026-06-21: Production Execution Integration

### Context
Implemented the physical manufacturing execution and rollback workflows of the Production module, introducing the ability to consume component materials and add finished/semi-finished goods yield.

### Key Engineering Decisions
1. **No Database-Level Unique Constraint on `production_order_id` in Executions**:
   * *Decision*: Avoid enforcing `UNIQUE(production_order_id)` on the `production_executions` table.
   * *Rationale*: Permits a production order to be executed, rolled back, corrected, and re-executed. We instead enforce a business logic guard ensuring that at most one execution remains in the `COMPLETED` status at any given time per order.
2. **Re-use `REVERSAL` Transaction Type**:
   * *Decision*: Avoid creating a new `PRODUCTION_REVERSAL` transaction type, re-using the existing `REVERSAL` enum value instead.
   * *Rationale*: Keeps transaction type enum manageable. Audit details are preserved via the linked `production_execution_id` foreign key and transaction `remarks`.
3. **Rollback Stock Consumption Guard**:
   * *Decision*: Prevent execution rollbacks if the finished/semi-finished goods output has already been consumed or dispatched (`output_inventory.quantity < execution.quantity_produced`).
   * *Rationale*: Ensures database integrity and prevents inventory records from going negative.
4. **Production Order Status Locking**:
   * *Decision*: Block `PATCH /production-orders/{id}/status` if the order is already in the `COMPLETED` or `CANCELLED` status. Validate allowed transitions via a strict state machine:
     * `DRAFT` -> `PLANNED`, `CANCELLED`
     * `PLANNED` -> `IN_PROGRESS`, `CANCELLED`
     * `IN_PROGRESS` -> `CANCELLED`
   * *Rationale*: Prevents bypassing the execution/rollback operations through direct status changes.
5. **No Unique Executions Concurrency (Deferred)**:
   * *Decision*: Concurrent execution race conditions are a known deferred v2 concern.

### Database Changes
* Created `production_executions` table with composite index `(production_order_id, status)`.
* Created `production_execution_items` table.
* Added nullable `production_execution_id` foreign key to the `inventory_transactions` table.
* Applied via Alembic migration revision `75dbc95f9297`.

### API Routes
* `POST /production-orders/{id}/execute` - Triggers production execution, mutates raw component and finished goods stocks, and logs transaction history.
* `POST /production-orders/{id}/rollback` - Reverts inventory stock additions/deductions and updates execution/order statuses.
* `GET /production-orders/{id}/executions` - Lists execution histories and line snapshots.


## 2026-07-11: Order Module Service Refactor

### Context
Extracted all business logic from `app/routes/order.py` into a new `OrderService` inside `app/services/order_service.py` to decouple business operations from the HTTP routing layer.

### Key Engineering Decisions
1. **Separation of Concerns**:
   * *Decision*: Moved `create_order`, `list_orders`, `get_order`, and `transition_status` entirely out of the router.
   * *Rationale*: Fat controllers prevent unit testing and reusability. Routes now strictly handle authentication, validation, calling the service, and returning schemas.
2. **Delegation of Domain Actions**:
   * *Decision*: Rather than stuffing all logic into one massive update status method, `transition_status` delegates to private domain helpers `_validate_transition`, `_dispatch_order`, and `_cancel_order`.
   * *Rationale*: Promotes DRY principles and keeps operations highly cohesive and easier to test individually.
3. **Single Transaction Boundary**:
   * *Decision*: Handled the `db.commit()` and `db.rollback()` within the main `transition_status` method rather than scattering it across helpers.
   * *Rationale*: Ensures that a dispatch or cancel operation succeeds or fails entirely atomically.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints preserved for `POST /orders/`, `GET /orders/`, `GET /orders/{id}`, and `PATCH /orders/{id}/status`.

## 2026-07-11: Purchase Order Module Service Refactor

### Context
Extracted all business logic from `app/routes/purchase_order.py` into a new `PurchaseOrderService` inside `app/services/purchase_order_service.py`, mirroring the `OrderService` architecture.

### Key Engineering Decisions
1. **Separation of Concerns**:
   * *Decision*: Moved `create_purchase_order`, `list_purchase_orders`, `get_purchase_order`, `transition_status`, and `receive_goods` entirely out of the router.
   * *Rationale*: Continues the migration away from fat controllers to a decoupled service layer.
2. **Delegation of Domain Actions**:
   * *Decision*: Used private helper methods like `_validate_transition` and `_process_receiving`.
   * *Rationale*: Keeps operations highly cohesive and easier to test individually.
3. **Single Transaction Boundary**:
   * *Decision*: `db.commit()` and `db.rollback()` are maintained within the orchestrating methods (`transition_status`, `receive_goods`) ensuring fully atomic database operations.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints and schemas preserved for all `/purchase-orders/` endpoints.

## 2026-07-11: Invoice Module Service Refactor

### Context
Extracted all business logic from `app/routes/invoice.py` into a new `InvoiceService` inside `app/services/invoice_service.py`, ensuring consistency with the `OrderService` and `PurchaseOrderService` architectures.

### Key Engineering Decisions
1. **Separation of Concerns**:
   * *Decision*: Moved `generate_invoice`, `list_invoices`, `get_invoice`, and `transition_status` entirely out of the router.
   * *Rationale*: Continues the migration away from fat controllers to a decoupled service layer.
2. **Delegation of Domain Actions**:
   * *Decision*: Used private helper methods like `_validate_order`, `_generate_invoice_number`, `_calculate_totals`, `_create_invoice_items`, and `_validate_transition`.
   * *Rationale*: Keeps operations highly cohesive and easier to test individually.
3. **Single Transaction Boundary**:
   * *Decision*: `db.commit()` and `db.rollback()` are maintained within the orchestrating methods (`generate_invoice`, `transition_status`) ensuring fully atomic database operations.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints and schemas preserved for all `/invoices/` endpoints.

## 2026-07-11: Post-Refactor Safety and Correctness Hotfixes

### Context
Addressed critical and high-priority correctness issues identified during the senior engineering architectural review.

### Key Engineering Decisions
1. **Transaction Safety Guards**:
   * *Decision*: Wrapped `OrderService.create_order` and `InvoiceService.generate_invoice` in outer `try/except Exception: db.rollback(); raise` blocks.
   * *Rationale*: Ensures that DB errors at the `db.commit()` stage do not leave SQLAlchemy sessions in a dirty, unrolled-back state.
2. **State Machine Completeness**:
   * *Decision*: Added `PARTIALLY_PAID` to `InvoiceService._validate_transition`.
   * *Rationale*: The payment route writes `PARTIALLY_PAID` to invoices. Without this, the invoice service would reject any future transitions.
3. **Payment Integrity**:
   * *Decision*: Added a guard in `create_payment` route to only accept invoices in `ISSUED` or `PARTIALLY_PAID` states.
   * *Rationale*: Prevents business-logic-violating payments against `DRAFT` or `CANCELLED` invoices.
4. **Concurrency-Safe Invoice Numbering**:
   * *Decision*: Replaced `COUNT(*) + 1` with an `IntegrityError` retry loop using the `max(id)` approach.
   * *Rationale*: Safely resolves race conditions under concurrency without requiring schema changes, sequences, or Alembic migrations.

## 2026-07-11: Payment Module Service Refactor

### Context
Extracted all business logic from `app/routes/payment.py` into a new `PaymentService` inside `app/services/payment_service.py`, maintaining full architectural consistency with existing services.

### Key Engineering Decisions
1. **Separation of Concerns**:
   * *Decision*: Moved `create_payment`, `list_payments`, `get_payment`, `invoice_summary`, `customer_summary`, `customer_invoices`, `outstanding_report`, and `aging_report` out of the router.
   * *Rationale*: Transforms the payment module into a domain service to further migrate towards a decoupled service layer.
2. **Strict Transaction Boundaries**:
   * *Decision*: Wrapped `create_payment` inside an outer `try/except Exception: db.rollback(); raise` block, mimicking the post-review safe transaction pattern established in earlier modules.
   * *Rationale*: Guarantees atomic database operations safely, handling both logical exceptions and ORM failures gracefully without leaking uncommitted state.
3. **Status Invariants Preserved**:
   * *Decision*: Included strict guards enforcing `ISSUED` and `PARTIALLY_PAID` conditions exactly as defined in the post-review invoice state machine.
   * *Rationale*: Ensures full compatibility with the existing InvoiceService module behavior.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints and schemas preserved for all `/payments/` endpoints.

## 2026-07-11: Production Module Service Refactor

### Context
Extracted all business logic from the most complex and high-risk module in the system, `app/routes/production_order.py`, into a new `ProductionService` inside `app/services/production_service.py`.

### Key Engineering Decisions
1. **Method Splitting**:
   * *Decision*: Split the massive inline blocks into distinct, highly focused private helpers (`_validate_parent_product`, `_get_active_bom`, `_snapshot_bom`, `_calculate_consumption`, `_consume_inventory`, `_add_finished_goods`, `_rollback_consumption`, `_rollback_finished_goods`).
   * *Rationale*: Dramatically improves testability and readability of production execution and rollback flows without changing behaviour.
2. **Strict Transaction Boundaries**:
   * *Decision*: Enforced exact outer `try/except` transaction wrapping for `create_production_order`, `transition_status`, `execute_production`, and `rollback_execution`. Removed inline rollbacks.
   * *Rationale*: Since production execution simultaneously touches `ProductionExecution`, `ProductionExecutionItem`, `Inventory` (consumption), `Inventory` (output), and generates `InventoryTransaction` records, an atomic transaction boundary is absolutely critical.
3. **Behavioral Invariance**:
   * *Decision*: Preserved exact inventory logic (e.g. creating inventory rows if they don't exist during rollback/execution, calculating missing stock).
   * *Rationale*: Avoided introducing unrequested features like reservations or multi-stage routing, keeping the API contract identical.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints and schemas preserved for all `/production-orders/` endpoints.

## 2026-07-11: BOM Module Service Refactor

### Context
Extracted all business logic from `app/routes/bom.py` into a new `BOMService` inside `app/services/bom_service.py`, continuing the migration toward a decoupled service layer.

### Key Engineering Decisions
1. **Separation of Concerns**:
   * *Decision*: Moved `create_bom`, `get_boms`, `get_active_bom_by_product`, `get_bom`, `update_bom`, and `activate_bom` out of the router.
   * *Rationale*: Transforms the BOM module into a domain service, enforcing that routers are strictly for HTTP concerns.
2. **Strict Transaction Boundaries**:
   * *Decision*: All write operations (`create_bom`, `update_bom`, `activate_bom`) were wrapped entirely within a single outer `try/except Exception: db.rollback(); raise` block.
   * *Rationale*: Prevents dirty sessions from unhandled ORM failures or validation errors inside the validation helpers.
3. **Behavioral Invariance**:
   * *Decision*: Existing private helpers `_validate_bom_constraints` and `_handle_active_bom_deactivation` were ported and incorporated without logic changes.
   * *Rationale*: Ensures full backward compatibility with BOM validation and version activation logic.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints and schemas preserved for all `/boms/` endpoints.

## 2026-07-11: Inventory Module Service Refactor

### Context
Extracted all business logic from `app/routes/inventory.py` into a new `InventoryService` inside `app/services/inventory_service.py`, marking the completion of the Service Layer migration for all operational modules.

### Key Engineering Decisions
1. **Separation of Concerns**:
   * *Decision*: Moved `get_inventory`, `get_low_stock`, `get_inventory_item`, `create_inventory`, and `update_inventory` out of the router.
   * *Rationale*: Transforms the Inventory module into a domain service, enforcing that all routers are strictly for HTTP concerns.
2. **Strict Transaction Boundaries**:
   * *Decision*: All write operations (`create_inventory`, `update_inventory`) were wrapped entirely within a single outer `try/except Exception: db.rollback(); raise` block.
   * *Rationale*: Prevents dirty sessions from unhandled ORM failures.

### Database Changes
* None. Preserved identical schema and Alembic migrations.

### API Routes
* Identical endpoints and schemas preserved for all `/inventory/` endpoints.

