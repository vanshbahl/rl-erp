# RL-ERP

A modern, scalable Enterprise Resource Planning (ERP) platform designed for manufacturing, distribution, and inventory-driven businesses.

RL-ERP centralizes business operations into a single system, enabling organizations to manage inventory, sales, purchasing, production, finance, customers, and reporting through an integrated web application.

---

## Overview

Businesses often rely on spreadsheets and disconnected software tools to manage critical operations. RL-ERP aims to provide a unified platform that improves visibility, efficiency, and decision-making across departments.

Key goals:

- Centralized business operations
- Real-time inventory visibility
- Production planning and tracking
- Sales and purchasing workflows
- Financial reporting
- User and permission management
- Data-driven decision making

---

## Features

### Inventory Management

- Stock tracking
- Warehouse management
- Inventory movements
- Batch and lot tracking
- Low-stock alerts

### Sales Management

- Customer management
- Quotations
- Sales orders
- Dispatch tracking
- Invoice generation

### Purchase Management

- Vendor management
- Purchase orders
- Goods receipt tracking
- Supplier analytics

### Production Management

- Bill of Materials (BOM)
- Production orders
- Work order tracking
- Material consumption
- Production reporting

### Finance & Reporting

- Revenue tracking
- Expense management
- Profitability analysis
- Business dashboards
- Exportable reports

### User Management

- Authentication
- Role-based access control
- Audit logging
- Activity tracking

---

## Architecture

```text
Frontend (React + TypeScript)
            │
            ▼
      FastAPI Backend
            │
            ▼
       PostgreSQL
```

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic

### Database

- PostgreSQL

### DevOps

- Git
- GitHub
- Docker (planned)
- CI/CD (planned)

---

## Project Structure

```text
RL-ERP/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database/
│   │   └── core/
│   │
│   ├── migrations/
│   ├── tests/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   │
│   └── public/
│
├── docs/
│
├── .env
├── .gitignore
└── README.md
```

---

## Local Development

### Clone Repository

```bash
git clone https://github.com/vanshbahl/rl-erp.git
cd rl-erp
```

---

### Backend Setup

Create virtual environment:

```bash
python -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```env
DATABASE_URL=postgresql://postgres:password@localhost/rlerp
```

Run backend:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

API Docs:

```text
http://localhost:8000/docs
```

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Roles & Permissions

### Super Administrator

- Full platform access
- User management
- System configuration

### Administrator

- Operational management
- Reporting access

### Inventory Manager

- Inventory operations
- Stock adjustments

### Sales Team

- Customer management
- Order processing

### Purchasing Team

- Vendor management
- Procurement workflows

### Production Team

- Manufacturing operations
- Production tracking

### Finance Team

- Financial reports
- Revenue and expense tracking

---

## Roadmap

### Phase 1

- Authentication
- User management
- Dashboard
- Inventory module

### Phase 2

- Sales module
- Purchasing module
- CRM functionality

### Phase 3

- Production management
- Manufacturing workflows
- BOM management

### Phase 4

- Finance module
- Analytics engine
- Advanced reporting

### Phase 5

- Mobile application
- Vendor portal
- Customer portal
- AI-assisted forecasting

---

## Testing

Run tests:

```bash
pytest
```

---

## Development Standards

### Branch Naming

```text
feature/module-name
bugfix/issue-name
hotfix/issue-name
```

### Commit Convention

```text
feat: add inventory dashboard

fix: resolve authentication bug

refactor: improve database structure
```

---

## Future Enhancements

- Multi-company support
- Multi-warehouse management
- Barcode integration
- QR code tracking
- Email notifications
- WhatsApp notifications
- GST/VAT support
- AI forecasting
- Demand planning
- Advanced analytics

---

## Author

Vansh Bahl

---

## License

This project is currently under active development.

All rights reserved.
