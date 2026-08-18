# RL-ERP — Project Status Audit

> **Audit Date:** 2026-08-18
> **Source of truth:** Repository code. Statuses verified by code inspection, not documentation.

---

## Module Completion Matrix

| Module | Backend | Frontend | Integration | Database | Overall |
|---|---|---|---|---|---|
| Auth (Login/Register) | ✅ | ✅ | ✅ | ✅ | ✅ |
| User Management (RBAC) | ✅ | 🔴 | 🟡 | ✅ | 🟡 |
| Products | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Customers | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Inventory | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Suppliers | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Sales Orders | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Invoices | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Payments | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Purchase Orders | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| BOM | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Production Orders | ✅ | 🔴 | 🔴 | ✅ | 🟡 |
| Dashboard | 🔴 | 🟡 | 🔴 | N/A | 🔴 |
| Reports / Analytics | 🔴 | 🔴 | 🔴 | N/A | 🔴 |
| Settings | 🔴 | 🔴 | 🔴 | N/A | 🔴 |

**Status Key:** ✅ Complete | 🟡 Partial | 🔴 Missing | ⚠️ Exists but broken/inconsistent

---

## Backend Module Detail

All backend modules follow: FastAPI router → Service layer → SQLAlchemy models.
Auth via `HTTPBearer` JWT. RBAC via `require_roles()` / `require_admin()`.

### Auth (`/auth`) — ✅ Complete
- `POST /auth/register` — creates users (default role: `staff`)
- `POST /auth/login` — verifies bcrypt hash, returns JWT bearer token
- `GET /users/me` — returns `{id, username, email}` (no `role` or `full_name`)

### Admin (`/admin`) — ✅ Complete
- `GET /admin/users`, `GET /admin/users/{id}`, `PUT /admin/users/{id}/role`, `DELETE /admin/users/{id}`
- All require `admin` role; self-deletion blocked

### Products (`/products`) — ✅ Complete
- Full CRUD + PATCH deactivate (soft-delete)
- Auto-creates `Inventory` row on product creation
- `product_type` enforced: `RAW_MATERIAL`, `FINISHED_GOOD`, `SEMI_FINISHED`, `PACKAGING`, `CONSUMABLE`
- Bug: `GET /products/` filters active only; `GET /products/{id}` returns inactive products too

### Customers (`/customers`) — ✅ Complete
- Full CRUD + soft-delete via `/deactivate`
- Fields: company_name, contact_person, phone, email, gst_number, address, city, state, pincode

### Inventory (`/inventory`) — ✅ Complete (with audit gap)
- List, low-stock (filterable by product_type and supplier_id), single item
- `PUT /inventory/{product_id}` — arbitrary quantity override does NOT write an audit transaction (breaks immutable ledger contract)

### Suppliers (`/suppliers`) — ✅ Complete
- Full CRUD + soft-delete

### Sales Orders (`/orders`) — ✅ Complete
- State machine: PENDING → PROCESSING → DISPATCHED → COMPLETED; CANCELLED from first three
- Dispatching deducts inventory, writes ORDER_DISPATCH log
- Cancelling DISPATCHED order restores inventory with ORDER_CANCEL log
- Bug: ORDER_DISPATCH and ORDER_CANCEL are raw strings — not in InventoryTransactionType enum

### Invoices (`/invoices`) — ✅ Complete (GST not applied)
- `POST /invoices/generate/{order_id}` — from DISPATCHED or COMPLETED orders only
- State machine: DRAFT → ISSUED → PARTIALLY_PAID → PAID; CANCELLED from first three
- Tax hardcoded to 0.0 — GST not calculated despite gst_rate on products
- Sequential invoice numbering: INV-000001, INV-000002, etc.

### Payments (`/payments`) — ✅ Complete (with N+1 issues)
- Payment against invoice; methods: CASH, BANK_TRANSFER, CHEQUE, UPI, CARD
- Outstanding report, aging report (0-30, 31-60, 61-90, 90+ day buckets)
- Over-payment blocked
- N+1: outstanding_report and aging_report query payments per-invoice in a loop

### Purchase Orders (`/purchase-orders`) — ✅ Complete (with N+1 issue)
- State machine: DRAFT → SENT → PARTIALLY_RECEIVED → RECEIVED; CANCELLED from first three
- `POST /purchase-orders/{id}/receive` — increments inventory, writes PURCHASE_RECEIPT transactions
- N+1: list endpoint queries items per-PO in a loop

### BOM (`/boms`) — ✅ Complete
- Full CRUD + activate; only one active BOM per product enforced
- Validates component types (RAW_MATERIAL, SEMI_FINISHED, PACKAGING); no self-reference; no duplicates

### Production Orders (`/production-orders`) — ✅ Complete
- State machine: DRAFT → PLANNED → IN_PROGRESS → COMPLETED; CANCELLED from first three
- Execution: deducts components, adds yield; only one active execution per order
- Rollback: reverses all inventory; validates yield is still in stock
- Component availability pre-check endpoint

---

## Frontend Module Detail

### What Exists
| Component | Path | Status |
|---|---|---|
| Landing page (marketing) | `/` | ✅ Fully implemented |
| Login / Register | `/login`, `/register` | ✅ API-connected, responsive auth forms |
| AppShell (sidebar + topbar) | `/app/*` | ✅ UI shell exists (no data) |
| Dashboard page | `/app/dashboard` | 🟡 Static placeholder, hardcoded zeros |
| All ERP module pages | `/app/products` etc. | 🔴 Missing entirely |

### Dead Navigation Links
These sidebar links are defined but have no corresponding routes or pages:
`/app/products`, `/app/customers`, `/app/suppliers`, `/app/purchases`, `/app/sales`,
`/app/inventory`, `/app/invoices`, `/app/reports`, `/app/settings`

### Infrastructure Available (mostly unused)
- Axios client with auth token injection, 401 auto-redirect
- React Query client configured
- Zustand auth store (login, logout, setUser, persisted to localStorage)
- Shadcn UI library: Button, Card, Badge, Dialog, Input, Select, Table, Avatar, Sheet, Tooltip, Skeleton, Sonner, Command, Popover, ScrollArea, Separator, DropdownMenu, Label
- TanStack Table installed but not used
- Recharts installed but not used
- Motion (Framer Motion v12) — landing page only

---

## Frontend ↔ Backend Integration

### Authentication Integration — ✅ Complete
- Axios uses the configured backend root URL and injects persisted bearer tokens.
- FastAPI CORS allows configured frontend origins (default: `http://localhost:5173`).
- Login, registration, session restoration via `/users/me`, protected `/app/*` routes, and centralized 401 cleanup are implemented.
- The authenticated user shape is `{id, username, email, role}` and AppShell displays username and role.

All non-auth ERP endpoints remain without connected frontend UI.

---

## Database & Migration Status

### Tables (20 total)
users, products, inventory, inventory_transactions, customers, orders, order_items,
invoices, invoice_items, payments, suppliers, purchase_orders, purchase_order_items,
boms, bom_items, production_orders, production_order_items, production_executions,
production_execution_items

### Migration Issues
- Baseline migration is an empty `pass` — original schema created outside Alembic
- 2 other migrations are also empty `pass` bodies
- Functional migrations exist from BOM onwards (properly scripted)
- `ORDER_DISPATCH` and `ORDER_CANCEL` transaction types written as raw strings — not in enum

---

## Known Bugs

| # | Severity | Issue |
|---|---|---|
| 1 | High | ORDER_DISPATCH/ORDER_CANCEL not in InventoryTransactionType enum |
| 2 | High | GET /products/{id} returns inactive products; list endpoint does not |
| 3 | Medium | N+1 queries in payment reports and PO list |
| 4 | Medium | Manual inventory PUT doesn't write audit transaction |
| 5 | Medium | GST hardcoded to 0 despite gst_rate field on products |
| 6 | Low | user_service.py is completely empty |
| 7 | Low | No pagination on any list endpoint |
| 8 | Low | datetime.utcnow() deprecated in Python 3.12+ |

---

## Technical Debt

| Category | Issue |
|---|---|
| No pagination | All list endpoints return full tables |
| No row-level locking | Race condition risk on concurrent inventory mutations |
| GST not applied | Invoice tax always zero |
| Enum inconsistency | ORDER_DISPATCH/ORDER_CANCEL raw strings |
| Empty migrations | 3 no-op migration files |
| N+1 queries | Payment reports, PO list |
| No domain types in frontend | types/api.ts has no Product, Order, Customer interfaces |
| No route guards | Unauthenticated access to /app/* |
| Dead stubs | user_service.py, features/auth/index.ts, hooks/index.ts empty |
| Command Palette stub | Rendered but contains no commands or data |
