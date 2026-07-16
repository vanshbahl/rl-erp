# Developer Guide

Welcome to the RL-ERP development team. This guide covers local setup, workflows, and conventions to get you onboarded quickly.

## 1. Local Setup

### Prerequisites
- Python 3.10+
- Node.js 20+ (for Frontend)
- PostgreSQL 14+
- Git

### Backend Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/vanshbahl/rl-erp.git
   cd rl-erp/backend
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost/rlerp
   TEST_DATABASE_URL=postgresql://postgres:password@localhost/rlerp_test
   SECRET_KEY=generate_a_secure_random_string
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   ```
5. **Database Initialization:**
   Ensure your local PostgreSQL server is running and the `rlerp` database exists.
   ```bash
   alembic upgrade head
   ```
6. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000` and Swagger docs at `http://localhost:8000/docs`.

### Frontend Setup
1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Environment Variables:**
   Copy `.env.example` to `.env` (ensure `VITE_API_URL=http://localhost:8000`).
4. **Run the development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`.

## 2. Development Workflow & Git

- **Never work directly on main.** Create feature branches (`feature/add-inventory-ledger`, `bugfix/fix-dispatch-calc`).
- **Commits:** Write descriptive commit messages. Suggest logical commit groups.
- **Pull Requests:** Keep PRs small and focused. One PR should equal one feature or bugfix. Do not mix unrelated improvements.
- **Approval:** Wait for approval before merging branches.

## 3. Backend Conventions

### Folder Architecture
- `app/routes/`: FastAPI endpoints. Only handles request validation and HTTP responses.
- `app/services/`: Core business logic. Where the actual work happens.
- `app/models/`: SQLAlchemy tables.
- `app/schemas/`: Pydantic V2 schemas for input/output validation.

### Coding Standards
- **Typing:** Use strict Python typing everywhere (`def func(name: str) -> bool:`).
- **Service Layer Pattern:** Never put database queries in `routes`. Routers must inject a DB session and pass it to a service class/function.
- **Transactions:** Complex operations (e.g., dispatching an order and mutating inventory) MUST be wrapped in a transaction block to prevent data corruption.
- **Naming:** 
  - Python variables/functions: `snake_case`
  - Python classes: `PascalCase`
  - SQL Tables: plural `snake_case` (e.g., `production_orders`)

### Adding a New Feature
1. **Model:** Define the table in `app/models/`.
2. **Migration:** Run `alembic revision --autogenerate -m "Add new feature"` and then `alembic upgrade head`.
3. **Schemas:** Create input/output Pydantic schemas in `app/schemas/`.
4. **Service:** Create the business logic in `app/services/`.
5. **Route:** Expose the service via `app/routes/` and register the router in `main.py`.
6. **Tests:** Write unit/integration tests in `tests/`.

## 4. Frontend Conventions

### Folder Architecture
- `src/components/ui/`: Reusable, generic Shadcn UI components.
- `src/features/`: Domain-specific components (e.g., `features/auth`, `features/inventory`).
- `src/pages/`: Route-level views.

### Coding Standards
- **Typing:** Strict TypeScript. Use `interface` or `type` for all props.
- **Data Fetching:** Use TanStack Query (React Query) for all API interactions. Do not use generic `useEffect` for data fetching.
- **State:** Use Zustand for client-side state.
- **Styling:** Use Tailwind CSS utility classes. Avoid writing custom `.css` files unless absolutely necessary for complex animations.

## 5. Testing Strategy
- The backend aims for >99% test coverage.
- The `TEST_DATABASE_URL` is used automatically by Pytest fixtures.
- Every test runs in an isolated transaction that rolls back afterward, ensuring tests never pollute the database.
- **To run tests:**
  ```bash
  cd backend
  pytest --cov=app --cov-report=term-missing
  ```

## 6. Debugging & Troubleshooting
- **Database Schema Sync Issues:** If you get `relation does not exist` errors, your database is out of sync. Run `alembic upgrade head`. If a migration was messed up locally, you may need to recreate the local DB and rerun migrations.
- **JWT Errors:** If you get `401 Unauthorized` constantly, check your `.env` file to ensure `SECRET_KEY` is set properly and the token hasn't expired.
- **Frontend CORS Errors:** Ensure the FastAPI backend has CORS middleware configured to allow `http://localhost:5173`.
