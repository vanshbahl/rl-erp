# State Management

## The Split State Architecture
RL-ERP completely separates UI state from Server state to prevent cache invalidation nightmares and bloated global stores.

### Server State (TanStack Query)
All data retrieved from the FastAPI backend is managed by React Query (`@tanstack/react-query`).
- **Why**: Automatic caching, background refetching, deduping, and optimistic updates.
- **Usage**: Every API endpoint will have a corresponding custom hook (e.g., `useProducts()`, `useCreateProduct()`).

### UI State (Zustand)
Global UI state is managed by Zustand.
- **Why**: Boilerplate-free, hooks-based, and highly performant.
- **Usage**: Used strictly for transient UI state that spans multiple components (e.g., `isSidebarOpen`, `activeModal`, `theme` overrides).

## Form State (React Hook Form + Zod)
Local form state is strictly managed by `react-hook-form` paired with `zod` for schema validation. We do not use controlled `useState` inputs for large forms to prevent unnecessary re-renders.
