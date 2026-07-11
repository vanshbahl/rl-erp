# System Architecture - RL-ERP

## 1. Overview
RL-ERP is built using a decoupled architecture separating the front-end user interface from the backend business logic and database.

```text
  [ Client User Interface ]
             │
             │ HTTP (JSON payloads / JWT auth)
             ▼
    [ FastAPI Routers ]
             │
             │ Calls Domain Services (e.g., OrderService)
             ▼
    [ Service Layer ]
             │
             │ SQLAlchemy ORM (PostgreSQL driver)
             ▼
     [ PostgreSQL DB ]
```

## 2. Module Relationships & Data Flow

* **Authentication**: Secures access via JWT. Users are assigned one of three roles (`admin`, `manager`, `staff`), which are checked dynamically at the route level via dependencies.
* **Products & Classification**: Central catalog. Products are classified (`FINISHED_GOOD`, `SEMI_FINISHED`, `RAW_MATERIAL`, `PACKAGING`, `CONSUMABLE`) and store Standard Costing metadata.
* **BOM & Recipes**: Finished/Semi-Finished products can have active Recipes (BOMs) specifying component products and their requirements.
* **Sales / Orders (Service Layer)**: Handled by `OrderService`. Customer orders deduct `FINISHED_GOOD` stock from the inventory module upon dispatch.
* **Procurement / PO**: Purchase orders issued to suppliers increment inventory stock upon receipts validation.
* **Production Orders (Planning)**: Schedules production runs. Pulls requirements from the active BOM, scales quantities based on target yield, checks raw materials stock levels in the inventory, and snapshots static requirement logs.
* **Production Execution**: Performs physical stock consumption and finished good additions, records execution audits, creates transaction history logs, and handles rollback operations.

## 3. Database ER Diagram

```mermaid
erDiagram
    customers ||--o{ orders : places
    products ||--|| inventory : "has quantity"
    orders ||--|{ order_items : contains
    products ||--o{ order_items : "referenced in"
    orders ||--o| invoices : billing
    customers ||--o{ invoices : receives
    invoices ||--|{ invoice_items : contains
    products ||--o{ invoice_items : "referenced in"
    invoices ||--o{ payments : collects
    suppliers ||--o{ purchase_orders : receives
    purchase_orders ||--|{ purchase_order_items : contains
    products ||--o{ purchase_order_items : "referenced in"
    products ||--o{ inventory_transactions : logs
    orders ||--o{ inventory_transactions : audits
    purchase_orders ||--o{ inventory_transactions : audits
    products ||--o{ boms : "has recipes"
    boms ||--|{ bom_items : contains
    products ||--o{ bom_items : "referenced as component"
    products ||--o{ production_orders : "scheduled for"
    boms ||--o{ production_orders : "based on"
    production_orders ||--|{ production_order_items : contains
    products ||--o{ production_order_items : "referenced as component"
    production_orders ||--o{ production_executions : executes
    production_executions ||--|{ production_execution_items : contains
    products ||--o{ production_execution_items : "referenced as component"
    production_executions ||--o{ inventory_transactions : logs
```
