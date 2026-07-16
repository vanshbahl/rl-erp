# Product Requirements Document (PRD)

## 1. Vision
RL-ERP aims to provide a centralized, modern, and scalable Enterprise Resource Planning (ERP) platform designed specifically for manufacturing, distribution, and inventory-driven businesses. By unifying business operations, RL-ERP eliminates the reliance on spreadsheets and disconnected software, delivering real-time visibility and efficiency across the entire manufacturing lifecycle.

## 2. Problem Statement
Small and medium manufacturing businesses struggle with disjointed operational data. When sales orders, raw material inventory, production jobs, and invoicing are handled in separate, non-integrated tools, data silos emerge. This leads to stockouts, delayed dispatches, unaccounted raw material consumption, and poor financial visibility.

## 3. Goals
- **Single Source of Truth:** Centralize customer management, product data, orders, production, inventory, and finance.
- **Traceability:** Provide full end-to-end traceability from raw material procurement to finished goods dispatch and final invoice payment.
- **Data Integrity:** Prevent negative inventory, ensure atomic transactions for production yields, and enforce strict state-machine lifecycles for orders and invoices.
- **Efficiency:** Automate the deduction of raw materials based on Bill of Materials (BOM) when production jobs execute.
- **Modern Experience:** Deliver a fast, responsive, and aesthetically premium user interface for both desktop and mobile web.

## 4. Non-Goals
- Human Resources (HR) or Payroll management modules.
- Direct e-commerce storefronts (B2C sales portals).
- Deep logistics routing (e.g., driver route optimization).

## 5. Target Users
- **Small to Medium Manufacturing Enterprises (SMEs):** Organizations producing finished goods from raw materials.
- **Distribution Businesses:** Companies that require strict inventory and dispatch control.

## 6. User Roles
- **Admin:** Full platform access, user management, and system overrides (e.g., forced rollbacks, inventory initialization).
- **Manager:** Operational management, production scheduling, inventory planning, and reporting access.
- **Staff:** View-level access, performing daily execution tasks like stock adjustments, order dispatch, and recording production yields.

## 7. Functional Requirements

### 7.1 Customer Management
- Create, read, update, and soft-delete customer entities.
- Store company name, contact details, GST number, and billing/shipping addresses.

### 7.2 Product Management
- Define products with categories: `RAW_MATERIAL`, `FINISHED_GOOD`, `SEMI_FINISHED`, `PACKAGING`, `CONSUMABLE`.
- Maintain standard costs, pricing, units of measurement, and default supplier links.

### 7.3 Order Management
- Create multi-item customer orders with auto-calculated totals.
- Track order lifecycle (`PENDING`, `PROCESSING`, `DISPATCHED`, `COMPLETED`, `CANCELLED`).
- Deduct inventory upon order dispatch and log inventory transactions.

### 7.4 Inventory Tracking
- Maintain separate ledger and counts for raw materials and finished goods.
- Expose low-stock alerts based on configurable minimum stock thresholds.
- Provide atomic transaction logging for every stock movement (`SALE`, `PURCHASE_RECEIPT`, `ADJUSTMENT`, `PRODUCTION_CONSUMPTION`, `PRODUCTION_OUTPUT`, `REVERSAL`, `ORDER_DISPATCH`, `ORDER_CANCEL`).

### 7.5 Bill of Materials (BOM) & Production
- Create and version BOMs linking finished goods to their raw material components.
- Generate Production Orders referencing active BOMs to snapshot required quantities.
- Execute production runs to atomically deduct raw components and increment finished yield.
- Provide a strict rollback mechanism for correcting erroneous production runs.

### 7.6 Purchasing
- Create Purchase Orders for suppliers (`DRAFT`, `SENT`, `PARTIALLY_RECEIVED`, `RECEIVED`).
- Receive goods against purchase orders to dynamically increment raw material inventory.

### 7.7 Invoicing & Payments
- Generate immutable invoices from dispatched orders.
- Record payments (`CASH`, `BANK_TRANSFER`, `CHEQUE`, `UPI`, `CARD`) against invoices.
- Track invoice payment status (`DRAFT`, `ISSUED`, `PARTIALLY_PAID`, `PAID`).
- Generate aging reports for overdue invoices.

## 8. Business Rules
1. **No Negative Inventory:** The system must block any action (dispatch, production) that would drive stock levels below zero.
2. **Immutable History:** Financial records, production executions, and order dispatches must write immutable logs. Modifications must be handled via explicit rollbacks or reversals.
3. **Strict Transitions:** Entities (Orders, Invoices, Production Orders) can only transition through their defined state machines. Skipping required states (e.g., `DRAFT` directly to `COMPLETED`) is prohibited.
4. **Active BOM Enforcement:** Only one BOM can be marked active per product at any given time.

## 9. Feature List (Current & Planned)
- ✅ Customer & Supplier Management
- ✅ Product & Inventory Module
- ✅ End-to-End Sales Order & Dispatch
- ✅ Purchase Orders & Goods Receipt
- ✅ BOM & Production Execution
- ✅ Invoicing & Payments Engine
- ✅ Service Layer Backend Architecture
- ⏳ Authentication (JWT) & RBAC
- ⏳ Dashboard Shell & Core UI
- ⏳ Analytics & Reporting (Cost variations, general ledger)

## 10. Future Roadmap
- Production Costing (Actual vs Standard variations).
- Complete comprehensive Inventory Ledger view.
- Multi-company and Multi-warehouse support.
- Automated email/WhatsApp notifications.
- General Ledger & Expense management.
