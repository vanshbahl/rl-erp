# Routing

## React Router v7
The frontend uses React Router v7 for client-side routing.

## Structure
The route configuration is defined in `src/app/router.tsx`.

### Public Routes
- **`/`**: The main Landing Page showcasing the ERP's capabilities.
- **`/login`**: Authentication entry point.
- **`/register`**: New user registration.

### Authenticated Routes (`/app/*`)
All routes under `/app` are wrapped in a `ProtectedRoute` (or `AppShell`) layout. This layout verifies the user's JWT state before rendering.

- **`/app/dashboard`**: The main user dashboard.
- *(Future modules will map to `/app/products`, `/app/inventory`, etc.)*

## Lazy Loading
To ensure the landing page remains blazing fast, the authenticated application modules are lazily loaded. The React Compiler handles fine-grained memoization across the component tree.
