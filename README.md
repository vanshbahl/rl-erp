# RL-ERP

A modern, scalable Enterprise Resource Planning (ERP) platform designed for manufacturing, distribution, and inventory-driven businesses.

RL-ERP centralizes business operations into a single robust backend system, enabling organizations to manage inventory, sales, purchasing, production, finance, and reporting efficiently.

---

## 📖 Core Documentation

For detailed guides and reference documentation, please consult the following master documents:

- **[Product Requirements Document (PRD)](PRD.md)**: Product vision, goals, and feature requirements.
- **[Technical Reference Document (TRD)](TRD.md)**: System architecture, tech stack, and design decisions.
- **[UI/UX Design](UI_UX_Design.md)**: Frontend design system, typography, and interaction guidelines.
- **[App Flow](App_Flow.md)**: User journeys and state-machine flow diagrams.
- **[Backend Schema](Backend_Schema.md)**: Database ERD, table structures, and ORM behaviors.
- **[Developer Guide](Developer_Guide.md)**: Local setup, git workflow, and coding conventions.

---

## 🚀 Overview

Businesses often rely on spreadsheets and disconnected software tools to manage critical operations. RL-ERP aims to provide a unified platform that improves visibility, efficiency, and decision-making across departments.

### Features
- **Inventory Management**: Stock tracking for raw materials and finished goods, low-stock alerts, and atomic transaction logs.
- **Sales Management**: Customer management, strictly-enforced order lifecycles, and automated dispatch-to-inventory deduction.
- **Purchase Management**: Supplier management, purchase order tracking, and seamless goods receipt.
- **Production Management**: Multi-version Bill of Materials (BOM), production job planning, scaleable material requirements, and yielding execution with rollback support.
- **Finance & Invoicing**: Automated invoice generation and multi-state payment tracking.
- **User Management & Security**: Secure JWT authentication and Role-Based Access Control (RBAC).

---

## 🖼️ Screenshots

*[Screenshots placeholder]*

---

## 💻 Tech Stack

### Backend
- **Framework**: Python 3.10+, FastAPI
- **Database ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic V2
- **Testing**: Pytest, Pytest-Asyncio, Factory-Boy (>99% coverage)
- **Security**: Passlib (Bcrypt), Python-JOSE (JWT)

### Database
- PostgreSQL 14+

### Frontend
- **Framework**: React 19 (Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4, shadcn/ui
- **State/Data**: Zustand, TanStack Query, Axios
- **Animations**: Framer Motion

---

## 🏗️ Architecture Overview

RL-ERP utilizes a highly decoupled backend architecture prioritizing data integrity and testability.

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

## 📁 Folder Structure

```text
RL-ERP/
├── backend/
│   ├── app/
│   │   ├── core/         # Config & security
│   │   ├── dependencies/ # Auth dependency injection
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # FastAPI endpoints
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   ├── tests/            # Pytest test suite
│   └── main.py           # Application entry point
├── frontend/
│   ├── src/              # React code
│   └── package.json
├── PRD.md                # Product Requirements
├── TRD.md                # Technical Reference
├── Developer_Guide.md    # Dev Onboarding
└── README.md
```

---

## 🛠️ Installation & Running Locally

Please see the **[Developer Guide](Developer_Guide.md)** for detailed, step-by-step installation instructions.

### Quick Start (Backend)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```
*API running at `http://localhost:8000`*

### Quick Start (Frontend)
```bash
cd frontend
npm install
npm run dev
```
*UI running at `http://localhost:5173`*

---

## ⚙️ Environment Variables

The backend requires a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://user:password@localhost/rlerp
TEST_DATABASE_URL=postgresql://user:password@localhost/rlerp_test
SECRET_KEY=your_secure_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🧰 Available Scripts

**Backend (`backend/`)**
- `uvicorn main:app --reload`: Start development server.
- `alembic upgrade head`: Run database migrations.
- `pytest`: Run test suite.
- `pytest --cov=app`: Run tests with coverage report.

**Frontend (`frontend/`)**
- `npm run dev`: Start development server.
- `npm run build`: Build production bundle.
- `npm run lint`: Run ESLint.

---

## 🌐 API Overview

The API is fully documented via Swagger. Once the backend is running, navigate to:
`http://localhost:8000/docs`

Core API route groupings include: `/auth`, `/users`, `/admin`, `/customers`, `/products`, `/inventory`, `/orders`, `/invoices`, `/payments`, `/suppliers`, `/purchase-orders`, `/boms`, and `/production-orders`.

---

## 🗄️ Database Overview

The PostgreSQL database enforces strict referential integrity. All state transitions (e.g., executing a production job) use transactional database locks and write immutable audit logs to the `inventory_transactions` table. See the **[Backend Schema](Backend_Schema.md)** document for full ERD and definitions.

---

## 🔒 Authentication

All API endpoints (except public health checks and login/register) are secured via stateless JWT tokens. Role-Based Access Control (RBAC) restricts endpoints based on user roles (`admin`, `manager`, `staff`).

---

## 📈 Project Status & Roadmap

The backend `v1.0` is complete and fully tested. The frontend shell and core modules are currently under active development.

### Upcoming
- Complete Frontend Dashboard Shell & Sidebar Navigation.
- Build React Modules for Inventory, Orders, and Production.
- Implement Production Costing (Actual vs Standard variations) in the backend.

---

## 🤝 Contributing

*[Contributing guidelines placeholder]*

---

## 📜 License

*[License placeholder]*

---
*Developed by Vansh Bahl*
