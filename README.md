# RL-ERP

A modern, scalable Enterprise Resource Planning (ERP) platform designed for manufacturing, distribution, and inventory-driven businesses.

RL-ERP centralizes business operations into a single robust backend system, enabling organizations to manage inventory, sales, purchasing, production, finance, and reporting efficiently.

---

## Overview

Businesses often rely on spreadsheets and disconnected software tools to manage critical operations. RL-ERP aims to provide a unified platform that improves visibility, efficiency, and decision-making across departments.

**Key capabilities:**
- Centralized business operations
- Real-time inventory visibility and transactions
- Manufacturing and production tracking
- End-to-end sales and purchasing workflows
- Financial invoicing and payment aging
- Robust RBAC (Role-Based Access Control)
- Highly decoupled Service Layer architecture

---

## Features

### Inventory Management
- Stock tracking for raw materials and finished goods
- Real-time inventory transactions and consumption tracking
- Reversal and rollback auditing
- Low-stock alerts and safety thresholds

### Sales Management
- Customer entity management
- Order lifecycle management with strict state machines
- Dispatch tracking tied directly to inventory deduction

### Purchase Management
- Supplier and vendor management
- Purchase order lifecycle tracking
- Goods receipt validation tied directly to inventory incrementation

### Production Management
- Multi-version Bill of Materials (BOM) management
- Production order planning and stock scaling
- Work order execution and rollback support
- Raw material consumption and finished goods yield tracking

### Finance & Invoicing
- Automated invoice generation from dispatched orders
- Multi-state payment tracking (DRAFT, ISSUED, PARTIALLY_PAID, PAID)
- Outstanding balances and aging reports

### User Management & Security
- Secure JWT-based authentication
- Role-based access control (Admin, Manager, Staff)
- API endpoint protection across all business layers

---

## Architecture

RL-ERP utilizes a highly decoupled, modern backend architecture prioritizing data integrity and testability.

```text
    [ Client User Interface ]
               │
               │ HTTP (JSON payloads / JWT auth)
               ▼
      [ FastAPI Routers ]
      (Data Validation & Auth)
               │
               │ Calls Domain Services
               ▼
       [ Service Layer ]
     (Atomic Business Logic)
               │
               │ SQLAlchemy ORM
               ▼
       [ PostgreSQL DB ]
```

---

## Technology Stack

### Backend
- **Framework**: Python 3.10+, FastAPI
- **Database ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic V2
- **Testing**: Pytest, Pytest-Asyncio, Factory-Boy
- **Security**: Passlib (Bcrypt), Python-JOSE (JWT)

### Database
- PostgreSQL

### Frontend
- **Framework**: React 19 (Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4, shadcn/ui
- **State/Data**: Zustand, TanStack Query, Axios
- **Animations**: Framer Motion (Restraint-focused)

---

## Project Structure

```text
RL-ERP/
│
├── backend/
│   ├── app/
│   │   ├── core/         # Config, database setup, security
│   │   ├── dependencies/ # Auth dependency injection
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # FastAPI endpoints (Controllers)
│   │   ├── schemas/      # Pydantic validation schemas
│   │   └── services/     # Decoupled business logic
│   │
│   ├── alembic/          # Database migrations
│   ├── tests/            # Pytest test suite (>99% coverage)
│   │   ├── unit/         # Isolated service and function tests
│   │   ├── integration/  # Multi-service business workflows
│   │   └── security/     # Penetration and boundary testing
│   │
│   └── main.py           # Application entry point
│
├── frontend/             # Next.js / Vite UI (Planned)
├── docs/                 # Technical documentation
└── README.md
```

---

## Local Development

### Clone Repository

```bash
git clone https://github.com/vanshbahl/rl-erp.git
cd rl-erp
```

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure Environment:**
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://postgres:password@localhost/rlerp
TEST_DATABASE_URL=postgresql://postgres:password@localhost/rlerp_test
SECRET_KEY=your_secure_random_string
```

4. **Initialize Database:**
```bash
alembic upgrade head
```

5. **Run Development Server:**
```bash
uvicorn main:app --reload
```

- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run Development Server:**
```bash
npm run dev
```

- **Frontend App**: `http://localhost:5173`

---

## Testing

RL-ERP features a robust testing infrastructure ensuring database isolation with transactions that rollback after each test. The suite includes complete unit, integration, and security tests achieving **>99% coverage**.

### Run tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app --cov-report=term-missing
```

---

## Roles & Permissions

- **Admin**: Full platform access, user management, systemic overrides.
- **Manager**: Operational management, production scheduling, reporting access.
- **Staff**: View access, stock adjustments, order dispatch, daily execution.

---

## Roadmap
### Completed (Backend v1.0)
- ✅ Core Auth & User Management
- ✅ Products & Inventory Module
- ✅ End-to-End Sales & Purchase Order Module
- ✅ Bill of Materials (BOM) & Production Execution
- ✅ Invoicing & Payments Engine
- ✅ Service Layer Architectural Refactoring
- ✅ Comprehensive Test Suite (>99% Coverage)
- ✅ Frontend Foundation & Build Pipeline
- ✅ Custom Theme Provider & Design System
- ✅ Premium Landing Page (Marketing)

### Upcoming (Frontend)
- JWT Authentication & Protected Routes
- Dashboard Shell & Sidebar Navigation
- Products & Inventory Modules
- Orders & Production Modules

### Upcoming (Backend v1.1)
- Production Costing (Actual vs Standard variations)
- Complete comprehensive Inventory Ledger
- Pagination & performance optimization

### Upcoming (Backend v2)
- Concurrent execution safe-guards
- Multi-company & Multi-warehouse support
- Automated email/WhatsApp notifications
- Expense management & General Ledger

---

## Author & License

**Vansh Bahl**

This project is currently under active development. All rights reserved.
