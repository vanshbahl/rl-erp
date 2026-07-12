# Folder Structure

The frontend strictly follows a modular, feature-based directory structure to support long-term scalability.

```text
frontend/
├── src/
│   ├── app/                    # Application shell, global providers, routing config
│   │   ├── providers.tsx
│   │   ├── router.tsx
│   │   └── ThemeProvider.tsx
│   │
│   ├── components/             # Reusable, domain-agnostic UI components
│   │   ├── ui/                 # Base shadcn/ui components
│   │   ├── animations/         # Reusable Framer Motion primitives
│   │   ├── simulations/        # High-fidelity dashboard & workflow simulators
│   │   └── layouts/            # Page layout wrappers (PublicLayout, AppShell)
│   │
│   ├── features/               # Business-specific modules (The core of the ERP)
│   │   ├── auth/               # Login, JWT parsing, AuthProvider
│   │   ├── products/           # Product catalog, variants, pricing
│   │   ├── inventory/          # Stock levels, warehouses, movements
│   │   └── customers/          # CRM, accounts, history
│   │
│   ├── lib/                    # Core utilities and configs
│   │   ├── api.ts              # Axios instance and interceptors
│   │   └── utils.ts            # Tailwind `cn` and formatting helpers
│   │
│   ├── pages/                  # Route entry components
│   │   ├── public/             # Landing page, login, register
│   │   │   └── sections/       # Landing page specific sections (Hero, Modules)
│   │   └── app/                # Authenticated dashboard and feature views
│   │
│   ├── styles/                 # Global styles
│   │   └── globals.css         # Tailwind v4 configuration and tokens
│   │
│   ├── types/                  # Global TypeScript interfaces
│   │
│   └── main.tsx                # React root entry point
```
