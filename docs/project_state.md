# Project State - RL-ERP

## Completed Modules
- **Authentication**: JWT validation, password hashing, and user dependencies.
- **User & Admin Management**: Roles configuration, admin routes.
- **Customer Management**: CRUD endpoints, soft-deactivate toggles.
- **Product Management**: CRUD endpoints, default inventory mapping, Product Classification (`RAW_MATERIAL`, `FINISHED_GOOD`, `SEMI_FINISHED`, `PACKAGING`, `CONSUMABLE`), and Raw Material Foundation (`standard_cost`, `default_supplier_id`).
- **Inventory Management**: Inventory tracking, adjustments, and low-stock alerting (`GET /inventory/low-stock`).
- **Bill of Materials (BOM)**: Recipe management for Finished and Semi-Finished Goods, dynamic version tracking, active recipe lookups (`GET /boms/product/{product_id}`), and line-item duplicate prevention constraints.
- **Order Management**: Order lifecycle, automatic finished goods inventory deduction on dispatch, transaction logs, cancellation rollback.
- **Invoice Module**: Invoice generation from dispatched/completed orders, subtotal/total calculation.
- **Payments Module**: Payments collection, balance summary, outstanding reports, aging report.
- **Supplier Module**: Supplier CRUD, deactivation.
- **Purchase Orders Module**: PO creation, receiving items and updating inventory.
- **Production Orders Module**: Production planning, BOM active version snapshotting, scaled component requirement lists, stock check availability, and status tracking (DRAFT, PLANNED, IN_PROGRESS, COMPLETED, CANCELLED).
- **Production Execution Module**: Physical stock consumption and yield output, execution history tracking, status protection, and rollback capability with finished yield consumption verification checks.

## In-Progress Modules
- None.

## Next Priorities
- **Inventory Ledger**: Complete movement logs audit trails.

## Known Issues
- No automated test suite implemented.
- Business logic is coupled directly to routes files (empty services layer).
