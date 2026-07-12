# Frontend Architecture

## Overview
RL-ERP uses a modern React 19 architecture built on Vite, emphasizing extreme performance, strict type safety, and modularity. The frontend is treated as a first-class citizen, fully decoupled from the FastAPI backend.

## Core Paradigms

### Feature-Sliced Design
The application is structured around specific business modules (Products, Customers, Inventory) rather than technical layers. This allows the ERP to scale infinitely without creating monolithic component or hook folders.

### API-First Data Layer
All data fetching and mutations are handled strictly by `@tanstack/react-query`. 
- Global state (Zustand) is strictly reserved for UI state (e.g., sidebar toggles, theme).
- Server state is exclusively managed by React Query.
- All API calls use a centralized Axios client with interceptors for JWT injection and token refresh.

### Theme & Styling
Styling is powered by Tailwind CSS v4 using the new `@theme` configuration block in CSS rather than `tailwind.config.js`. 
- Color space: OKLCH for perceptually uniform themes.
- Dark mode is handled by a custom `ThemeProvider` utilizing the native `document.startViewTransition` API for seamless circular wipe transitions, replacing `next-themes`.

### Client-Side Routing
Routing uses React Router v7. 
- Public routes (Landing Page, Login, Register) are separated from Authenticated routes (`/app/*`).
- Authenticated routes are wrapped in a `ProtectedRoute` component that verifies JWT validity before rendering.
