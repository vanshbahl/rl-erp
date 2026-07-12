# Project State: RL-ERP Backend

This document captures the current implementation state of the RL-ERP backend codebase, including implemented modules, API routes, service patterns, current architecture, missing modules, and technical debt as of July 2026.

---

## 1. Implemented Modules (100% Backend v1.0 Core Completion)

The backend contains the following fully operational and tested business modules:

1. **Authentication & Identity (`app/routes/auth.py`, `app/dependencies/auth.py`)**
   * Password hashing via `bcrypt` (using `passlib`).
   * JWT-based access token generation and validation (using `jose`).
   * Authentication dependencies (`get_current_user`, `require_admin`, `require_roles`) to secure endpoints.
2. **User & Admin Management (`app/routes/user.py`, `app/routes/admin.py`)**
   * Fetch current user profile.
   * Admin-only actions: listing all users, fetching specific users, deleting users (with self-deletion protection), and updating user roles (`admin`, `manager`, `staff`).
3. **Customer Management (`app/routes/customer.py`)**
   * CRUD operations for customers.
   * Soft-deactivation status toggles (`is_active = False`).
4. **Product Management (`app/routes/product.py`)**
   * CRUD operations for products.
   * **Product Classification**: Classified products into one of five types (`RAW_MATERIAL`, `FINISHED_GOOD`, `SEMI_FINISHED`, `PACKAGING`, `CONSUMABLE`), with type-specific validation and database mapping.
   * **Raw Material Foundation**: Added `standard_cost` tracking and `default_supplier_id` (default supplier link) metadata.
   * Auto-creation of a default inventory record (initial stock/minimum stock = 0) whenever a product is created.
   * Soft deactivation (`is_active = False`) and hard deletion capabilities.
5. **Inventory Management (`app/services/inventory_service.py`, `app/routes/inventory.py`)**
   * Tracking inventory for finished goods and raw materials.
   * Retrieving stock levels (all products or individual products).
   * **Low-Stock Reporting**: Dedicated endpoint returning records where current stock is below safety thresholds, supporting `product_type` and `supplier_id` filters.
   * Direct stock updates and record initialization.
6. **Order Management & Fulfillment (`app/services/order_service.py`, `app/routes/order.py`)**
   * Multi-item order creation with total amount auto-calculation.
   * Retrieving orders and order details.
   * **Order Status Lifecycle Validation & Inventory Integration**:
     * Strict state machine transitions (e.g. `PENDING` $\rightarrow$ `PROCESSING` $\rightarrow$ `DISPATCHED` $\rightarrow$ `COMPLETED`).
     * Transitioning to `DISPATCHED` automatically validates stock availability, deducts finished goods inventory, and logs transaction records of type `"ORDER_DISPATCH"`.
     * Transitioning to `CANCELLED` from `DISPATCHED` restores the inventory quantities and logs transaction records of type `"ORDER_CANCEL"`.
     * Completed orders are locked and cannot be modified.
7. **Invoice Management (`app/services/invoice_service.py`, `app/routes/invoice.py`)**
   * Invoice generation from orders that are in `DISPATCHED` or `COMPLETED` states (restricted to one invoice per order).
   * Auto-generation of sequential invoice numbers (format: `INV-XXXXXX`) using concurrency-safe integrity loop.
   * Invoice status transitions (e.g. `DRAFT` $\rightarrow$ `ISSUED` $\rightarrow$ `PAID` / `PARTIALLY_PAID` / `CANCELLED`).
8. **Payments & Cashflow (`app/services/payment_service.py`, `app/routes/payment.py`)**
   * Recording payments against invoices (validating that the payment amount does not exceed the outstanding balance).
   * Automatic invoice status updates: transitioning invoices to `PAID` when fully settled, or `PARTIALLY_PAID` if a balance remains.
   * Customer and invoice payment summaries, aging reports (bucketing invoices into current, 0-30, 31-60, 61-90, and 90+ days overdue), and outstanding invoice tracking.
9. **Supplier Management (`app/routes/supplier.py`)**
   * CRUD operations for suppliers.
   * Soft-deactivation status toggles (`is_active = False`).
10. **Purchase Orders (`app/services/purchase_order_service.py`, `app/routes/purchase_order.py`)**
    * PO creation in `DRAFT` status with line items, rate, quantity, and total amount auto-calculation.
    * PO status updates (e.g. `DRAFT` $\rightarrow$ `SENT` $\rightarrow$ `PARTIALLY_RECEIVED` $\rightarrow$ `RECEIVED` / `CANCELLED`).
    * **Fulfillment & Receiving**: Endpoints to receive goods against PO items, incrementing inventory, updating received quantities on the PO items, and writing transaction logs of type `"PURCHASE_RECEIPT"`.
11. **Bill of Materials (BOM) (`app/services/bom_service.py`, `app/routes/bom.py`)**
    * Recipe mapping for Finished Goods and Semi-Finished Goods.
    * Validations enforcing component product types, deactivating old active recipes, and blocking direct self-references.
    * Database unique constraints preventing duplicate component line items on a single recipe.
12. **Production Orders (`app/services/production_service.py`, `app/routes/production_order.py`)**
    * Create and list production orders (jobs) targeting a Finished or Semi-Finished product.
    * Resolves and snapshots the active BOM version on creation, scaling required component quantities.
    * Track lifecycle status updates (`DRAFT`, `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`) with automatic `status_changed_at` updates.
13. **Production Execution (`app/services/production_service.py`, `app/routes/production_order.py`)**
    * Handles physical inventory movements (raw material/packaging consumption and finished goods yield additions) tied to production orders.
    * Enforces database transaction atomicity, stock availability checks, and finished goods inventory auto-initialization.
    * Logs detailed inventory transactions (`PRODUCTION_CONSUMPTION`, `PRODUCTION_OUTPUT`) linking movements to executions.
    * Supports full operational rollbacks (restoring raw components, removing output yields, creating `REVERSAL` transaction logs) with safety guards preventing rollback if output goods have already been consumed.

---

## 2. API Routes

| Module | HTTP Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | POST | `/auth/register` | Public | Register a new user |
| | POST | `/auth/login` | Public | Login to retrieve JWT access token |
| **Users** | GET | `/users/me` | Logged In | Get current user's profile |
| **Admin** | PUT | `/admin/users/{user_id}/role` | Admin | Update user role |
| | GET | `/admin/users` | Admin | List all registered users |
| | GET | `/admin/users/{user_id}` | Admin | Get details of a specific user |
| | DELETE | `/admin/users/{user_id}` | Admin | Delete a user (cannot delete self) |
| **Customers** | GET | `/customers/` | Admin, Manager | Retrieve all active customers |
| | POST | `/customers/` | Admin, Manager | Create a new customer |
| | GET | `/customers/{customer_id}` | Admin, Manager | Get details for a specific customer |
| | PUT | `/customers/{customer_id}` | Admin, Manager | Update customer info |
| | PATCH | `/customers/{customer_id}/deactivate` | Admin | Deactivate a customer (soft delete) |
| **Products** | GET | `/products/` | Public | Retrieve active products |
| | POST | `/products/` | Admin, Manager | Create product + default inventory |
| | GET | `/products/{product_id}` | Public | Get product details |
| | PUT | `/products/{product_id}` | Admin, Manager | Update product |
| | PATCH | `/products/{product_id}/deactivate`| Admin | Deactivate a product (soft delete) |
| | DELETE | `/products/{product_id}` | Admin | Delete a product (hard delete) |
| **Inventory** | GET | `/inventory/` | Admin, Manager, Staff | Retrieve all inventory stock records |
| | GET | `/inventory/{product_id}` | Admin, Manager, Staff | Retrieve inventory for a specific product |
| | POST | `/inventory/` | Admin | Initialize inventory record |
| | PUT | `/inventory/{product_id}` | Admin, Manager | Adjust inventory stock quantities |
| | GET | `/inventory/low-stock` | Admin, Manager, Staff | Get low stock alert records |
| **Orders** | POST | `/orders/` | Admin, Manager | Create order with line items |
| | GET | `/orders/` | Admin, Manager, Staff | List all orders |
| | GET | `/orders/{order_id}` | Admin, Manager, Staff | Get order details with items |
| | PATCH | `/orders/{order_id}/status` | Admin, Manager | Update status, handles inventory dispatch/reversals |
| **Invoices** | POST | `/invoices/generate/{order_id}`| Admin, Manager | Generate invoice from order |
| | GET | `/invoices` | Admin, Manager, Staff | List all invoices |
| | GET | `/invoices/{invoice_id}` | Admin, Manager, Staff | Get invoice details with items |
| | PATCH | `/invoices/{invoice_id}/status` | Admin, Manager | Update invoice status with transition checks |
| **Payments** | POST | `/payments` | Admin, Manager | Record invoice payment & update invoice status |
| | GET | `/payments` | Admin, Manager | List all payments (newest first) |
| | GET | `/payments/{payment_id}` | Admin, Manager | Get individual payment details |
| | GET | `/payments/invoice/{invoice_id}/summary`| Admin, Manager | Get invoice balance and payment summary |
| | GET | `/payments/customer/{customer_id}/summary`| Admin, Manager | Get customer-wide invoiced, paid, and balance summary |
| | GET | `/payments/customer/{customer_id}/invoices`| Admin, Manager | Retrieve invoice breakdown for a customer |
| | GET | `/payments/outstanding` | Admin, Manager | List invoices with unpaid balances |
| | GET | `/payments/aging-report` | Admin, Manager | Generate outstanding balances overdue aging buckets |
| **Suppliers** | POST | `/suppliers` | Admin, Manager | Create a supplier record |
| | GET | `/suppliers` | Admin, Manager | Retrieve active suppliers |
| | GET | `/suppliers/{supplier_id}` | Admin, Manager | Get supplier details |
| | PUT | `/suppliers/{supplier_id}` | Admin, Manager | Update supplier information |
| | DELETE | `/suppliers/{supplier_id}` | Admin, Manager | Deactivate supplier (soft delete) |
| **Purchase Orders**| POST| `/purchase-orders` | Admin, Manager | Create a purchase order with items |
| | GET | `/purchase-orders` | Admin, Manager | List all purchase orders |
| | GET | `/purchase-orders/{purchase_order_id}`| Admin, Manager | Get purchase order details with items |
| | PATCH| `/purchase-orders/{purchase_order_id}/status`| Admin, Manager| Change PO status |
| | POST | `/purchase-orders/{purchase_order_id}/receive`| Admin, Manager| Receive goods (adds to inventory) |
| **Bill of Materials**| POST| `/boms` | Admin, Manager | Create a BOM and nested items |
| | GET | `/boms` | Admin, Manager, Staff | List all BOM headers |
| | GET | `/boms/{id}` | Admin, Manager, Staff | Get BOM details with nested items |
| | PUT | `/boms/{id}` | Admin, Manager | Replace BOM metadata and items |
| | PATCH | `/boms/{id}/activate` | Admin, Manager | Activate a specific BOM and deactivate others |
| | GET | `/boms/product/{product_id}`| Admin, Manager, Staff | Get the active BOM for a product |
| **Production Orders** | POST | `/production-orders` | Admin, Manager | Create a production order and snapshot scaled items |
| | GET | `/production-orders` | Admin, Manager, Staff | List all production order headers |
| | GET | `/production-orders/{id}` | Admin, Manager, Staff | Get production order details and requirements |
| | PATCH | `/production-orders/{id}/status` | Admin, Manager | Update production order status with strict transition rules |
| | GET | `/production-orders/{id}/check-availability` | Admin, Manager, Staff | Compare required component quantities against inventory |
| | POST | `/production-orders/{id}/execute` | Admin, Manager | Execute production run, mutating inventory and logging transactions |
| | POST | `/production-orders/{id}/rollback` | Admin, Manager | Rollback production run, restoring inventory and logging reversals |
| | GET | `/production-orders/{id}/executions` | Admin, Manager, Staff | Retrieve execution run history and material snapshot details |
| **Health** | GET | `/Health` | Public | System health check endpoint |

---

## 3. Services Layer Status

* **Status**: **Complete**
* **Details**: A `services` directory exists and contains `order_service.py`, `purchase_order_service.py`, `invoice_service.py`, `payment_service.py`, `production_service.py`, `bom_service.py`, and `inventory_service.py` which handle all business logic for their respective modules. All operational modules have been cleanly extracted and encapsulated within their respective domain services.

---

## 4. Current Architecture

```text
       Client (HTTP requests with JWT headers)
                      │
                      ▼
             FastAPI Application
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Dependencies                 Router Handlers
  (DB session, auth checks,    (Pydantic validation, call Services)
   role authorization)          
        │                           │
        └─────────────┬─────────────┘
                      ▼
               Service Layer
        (Atomic Business Operations)
                      │
                      ▼
               PostgreSQL DB
```

* **API Framework**: FastAPI, structuring routes inside APIRouters with prefixes and tags.
* **ORM**: SQLAlchemy 2.0 (using standard `declarative_base` model structures).
* **Database migrations**: Alembic versioned migration workflow.
* **Authentication**: JWT token-based security via `jose` and `passlib` (using bcrypt password hash algorithms).
* **Access Control**: Role-based decorators verifying user roles (`admin`, `manager`, `staff`).

---

## 5. Missing Modules & Major Architectural Gaps

1. **Expense Management & General Ledger**
   * No accounting ledger, financial accounts, charts of accounts, or expense tracking.
2. **Reporting Engine**
   * No dedicated reporting tables, reporting services, or export functions (e.g. PDF/Excel generation). Aging reports and summaries are calculated ad-hoc in endpoints.
3. **Frontend Integration (In Progress)**
   * The frontend foundation is complete (React 19, Vite, Tailwind v4, custom ThemeProvider).
   * Premium Landing Page marketing site and interactive simulators are fully built.
   * Core ERP module integration (Dashboard, Products, Auth) is pending.

---

## 6. Technical Debt

1. **Implicit/Missing SQLAlchemy Relationships**
   * Some foreign keys are defined across models, but explicit SQLAlchemy relationships (e.g. back-references from `Order` to `OrderItem`, `Customer` to `Order`) are missing on older tables. 
2. **No Seed Scripts**
   * There are no database seed scripts or mock data generators to quickly set up environments for local manual testing (though pytest factories mitigate this for automated testing).
3. **Incomplete Alembic Migration Graph**
   * Early tables were created outside Alembic or are baselined without table definitions in `baseline_existing_schema.py`. Certain migrations are empty files, making cold setups reliant on manual db initialization or schema synchronization issues.

---

## 7. Current Milestone & Next Priorities

1. **Frontend Authentication**: Implement `/login` and `/register` flows and integrate with the backend JWT endpoints.
2. **Frontend Dashboard Shell**: Build the authenticated `/app` layout, sidebar navigation, and routing.
3. **Production Costing (Backend Milestone)**: Capture standard and actual cost variations based on snapshotted standard material cost * component quantity consumed vs. output yield.
