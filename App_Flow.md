# Application Flow

This document details every major user workflow in the RL-ERP application.

## 1. Authentication Flow
The system uses JWT-based stateless authentication.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Enter Email & Password
    Frontend->>Backend: POST /auth/login
    Backend->>Database: Verify User & Hash
    Database-->>Backend: User Data (Role)
    Backend-->>Frontend: Returns JWT Access Token
    Frontend->>Frontend: Store Token in memory/localStorage
    Frontend->>User: Redirect to /app/dashboard
```

## 2. Order Fulfillment Flow
The complete journey of a customer order from creation to dispatch. Note that dispatching automatically handles inventory validation and deduction.

```mermaid
flowchart TD
    A[Create Order] -->|DRAFT| B(Add Order Items)
    B -->|Confirm| C{Status: PENDING}
    C -->|Start Processing| D{Status: PROCESSING}
    D -->|Dispatch Action| E{Stock Available?}
    E -->|No| F[Error: Insufficient Stock]
    E -->|Yes| G[Deduct Finished Goods Inventory]
    G --> H[Log TRANSACTION: ORDER_DISPATCH]
    H --> I{Status: DISPATCHED}
    I -->|Mark Complete| J{Status: COMPLETED}
    I -->|Cancel/Rollback| K[Restore Inventory & Log REVERSAL]
```

## 3. Production Workflow (BOM & Execution)
This flow tracks how raw materials are converted into finished goods.

```mermaid
flowchart TD
    A[Create Production Order] --> B(Select Active BOM)
    B --> C[System snapshots BOM component requirements]
    C --> D{Status: PLANNED}
    D --> E{Status: IN_PROGRESS}
    E --> F[User clicks Execute]
    F --> G{Components in Stock?}
    G -->|No| H[Error: Insufficient Raw Materials]
    G -->|Yes| I[Deduct Raw Material Inventory]
    I --> J[Increment Finished Goods Yield]
    J --> K[Log TRANSACTIONS: CONSUMPTION & OUTPUT]
    K --> L{Status: COMPLETED}
```

## 4. Invoicing and Payment Flow
Financial lifecycle tracking linked directly to dispatched orders.

```mermaid
flowchart TD
    A[Order is DISPATCHED or COMPLETED] --> B[Generate Invoice]
    B --> C{Status: DRAFT}
    C -->|Send to Customer| D{Status: ISSUED}
    D --> E[Record Payment]
    E --> F{Payment Amount?}
    F -->|Partial Balance| G{Status: PARTIALLY_PAID}
    F -->|Full Balance| H{Status: PAID}
    G --> E
```

## 5. Procurement Flow (Purchase Orders)
Procuring raw materials from suppliers.

```mermaid
flowchart TD
    A[Create Purchase Order] --> B(Add Raw Material Items)
    B --> C{Status: DRAFT}
    C -->|Send to Vendor| D{Status: SENT}
    D --> E[Receive Goods action]
    E --> F[Increment Raw Material Inventory]
    F --> G[Log TRANSACTION: PURCHASE_RECEIPT]
    G --> H{All Items Received?}
    H -->|No| I{Status: PARTIALLY_RECEIVED}
    H -->|Yes| J{Status: RECEIVED}
    I --> E
```

## 6. Inventory Ledger Flow
All modules eventually route inventory mutations through a central ledger transaction system to maintain an immutable audit trail.

```mermaid
flowchart LR
    PO[Purchase Receipt] -->|Adds| INV[(Inventory Table)]
    PO -->|Logs| LEDGER[Inventory Transactions]
    
    DISPATCH[Order Dispatch] -->|Subtracts| INV
    DISPATCH -->|Logs| LEDGER
    
    PROD_IN[Production Consumption] -->|Subtracts| INV
    PROD_IN -->|Logs| LEDGER
    
    PROD_OUT[Production Yield] -->|Adds| INV
    PROD_OUT -->|Logs| LEDGER
    
    MANUAL[Manual Adjustment] -->|Adds/Subtracts| INV
    MANUAL -->|Logs| LEDGER
```

## 7. Error Handling Flow
When a user attempts an invalid action (e.g., executing a production job without stock).

1. **User Action:** Clicks "Execute" in the Frontend.
2. **Frontend Request:** Dispatches `POST /production-orders/{id}/execute`.
3. **Backend Validation:** Service layer identifies a stock deficit.
4. **Backend Response:** Raises `HTTPException` with status `400 Bad Request` and detail `"Insufficient inventory for product ID X"`.
5. **Frontend Interceptor:** Axios catches the `400` error.
6. **User Feedback:** A red toast notification appears globally: "Insufficient inventory for product ID X". No page reload occurs.
