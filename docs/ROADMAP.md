# RL-ERP Development Roadmap

> Based on code audit of 2026-08-18. Reflects current implementation state.

---

## P0 — Authentication & Integration Foundation — ✅ Complete

- Configured CORS through `FRONTEND_ORIGINS` (default: `http://localhost:5173`).
- Aligned the Axios base URL to the unversioned FastAPI routes.
- Standardized the authenticated user as `{id, username, email, role}` and exposed `role` from `/users/me`.
- Added explicit runtime dependencies for JWT, password hashing, Alembic, and email validation.
- Added login/register pages, session restoration, protected routes, centralized 401 logout, and lightweight API error feedback.

The next priority is P1.1 Products. The existing migration-chain issue remains outside this phase and must be resolved before a clean database bootstrap can be relied upon.

---

## P1 — Core ERP Frontend (First Working Modules)

These are the foundational ERP pages needed to make the system usable. Implement in this order based on dependencies.

### P1.1 — Products Module
**Why:** Products are the master data that every other module depends on.
**Frontend:** Products list page (table, search, filter by type), create/edit product form, product detail view.
**Backend:** None needed. Backend is complete.

### P1.2 — Inventory Module
**Frontend:** Inventory list page (quantity, minimum stock, low-stock highlighting), edit minimum stock threshold, manual quantity adjustment (with audit log consideration).

### P1.3 — Customers Module
**Frontend:** Customer list, create/edit customer form, customer detail with order history.

### P1.4 — Suppliers Module
**Frontend:** Supplier list, create/edit supplier form.

### P1.5 — Sales Orders Module
**Frontend:** Order list (with status badges and filters), create order form (line items, customer, PO number), order detail view with status transition buttons.
**Backend:** None needed. Backend is complete.

### P1.6 — Invoices Module
**Frontend:** Invoice list, invoice detail view, status transition (DRAFT → ISSUED), payment recording form.

### P1.7 — Live Dashboard
**Frontend:** Replace hardcoded zeros in `DashboardPage.tsx` with React Query hooks fetching real data (pending orders count, low-stock alerts, outstanding AR).
**Backend:** May need a dedicated `/dashboard/summary` endpoint to avoid multiple round trips.

---

## P2 — Procurement & Manufacturing Frontend

### P2.1 — Purchase Orders Module
**Frontend:** PO list, create PO form, PO detail with receive goods action (partial receipt support).

### P2.2 — BOM Module
**Frontend:** BOM list per product, create/edit BOM form with dynamic component rows, version history, activate/deactivate toggle.

### P2.3 — Production Orders Module
**Frontend:** Production order list, create PO form, component availability check view, status transitions, execute/rollback with confirmation dialog.

### P2.4 — Payment & AR Reports
**Frontend:** Outstanding invoices report table, aging report with bucket visualization (can use Recharts — already installed).

### P2.5 — Command Palette
**Frontend:** Wire `CommandPalette.tsx` to navigation commands (jump to Products, Orders, etc.) and search by customer/product name.

---

## P3 — Advanced Features & Hardening

### P3.1 — GST Calculation
**Why:** Invoice tax is hardcoded to 0. The `gst_rate` field on products is unused.
**Backend:** Implement per-line-item GST calculation in `InvoiceService._calculate_totals()`. Likely requires adding GST breakdown to `InvoiceItem` model.
**Database:** Migration to add `tax_rate` and `tax_amount` columns to `invoice_items`.

### P3.2 — Inventory Audit Fixes
**Backend:** `PUT /inventory/{product_id}` should write an `ADJUSTMENT` transaction. Add `ORDER_DISPATCH` and `ORDER_CANCEL` to `InventoryTransactionType` enum.

### P3.3 — Pagination
**Backend:** Add `skip: int = 0, limit: int = 50` query params to all list endpoints.
**Frontend:** Implement cursor/offset pagination in table views.

### P3.4 — Fix N+1 Queries
**Backend:** Refactor `outstanding_report`, `aging_report`, and PO list using SQLAlchemy `joinedload` or aggregated subqueries.

### P3.5 — Row-Level Locking
**Backend:** Add `SELECT ... FOR UPDATE` to inventory mutations in `_dispatch_order`, `_consume_inventory`, and PO receipt to prevent concurrent stock corruption.

### P3.6 — Production Costing
**Backend:** Track actual material cost at execution time using `standard_cost` from products. Report variance between actual and standard cost.

### P3.7 — Inventory Transaction Ledger View
**Frontend:** Read-only table of all `inventory_transactions` for a product — the full audit trail.

### P3.8 — User Management UI (Admin)
**Frontend:** Admin-only users list, role change dropdown.

### P3.9 — Multi-company / Multi-warehouse
**Future:** Not scoped but architectural consideration for data isolation.

### P3.10 — Automated Notifications
**Future:** Email/WhatsApp on low stock, invoice due, PO receipt.

---

## Dependency Map

```
P0 (Foundation fixes) → P1 (Core modules) → P2 (Procurement/Manufacturing) → P3 (Advanced)
                                 ↑
                         Must be done in order:
                         Products → Inventory → Customers/Suppliers → Orders → Invoices
```

Products must exist before Orders can reference them.
Orders must be dispatched before Invoices can be generated.
BOMs must be created before Production Orders can be raised.
