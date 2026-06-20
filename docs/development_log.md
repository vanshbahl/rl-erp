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

