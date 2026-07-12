# API Integration

## Overview
Communication with the FastAPI backend is handled via a centralized Axios instance located in `src/lib/api.ts`.

## Axios Configuration
- **Base URL**: Configured via Vite environment variables (`import.meta.env.VITE_API_URL`).
- **Interceptors**: 
  - **Request**: Automatically injects the JWT `Authorization: Bearer <token>` into the headers for every request.
  - **Response**: Handles global error catching (e.g., redirecting to `/login` on a 401 Unauthorized response).

## Type Safety
The backend exposes OpenAPI schemas. The frontend TypeScript interfaces should closely mirror the backend Pydantic models to ensure end-to-end type safety. 

*(Note: Future iterations may introduce an automated OpenAPI-to-TypeScript client generator if the schema complexity warrants it.)*

## Data Fetching
As outlined in `state_management.md`, actual consumption of the Axios API endpoints within React components must go through TanStack Query to leverage caching and lifecycle management.
