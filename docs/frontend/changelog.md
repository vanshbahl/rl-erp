# Frontend Changelog

## 2026-07-12
### Added
- Created custom View Transitions `ThemeProvider` to replace `next-themes`.
- Implemented `AuroraBackground`, `Spotlight`, `Magnet`, and `Noise` Framer Motion primitives.
- Built timeline-based `DashboardSimulator` and interactive SVG `WorkflowVisualization`.
- Assembled full premium `LandingPage` with modular sections (`Hero`, `Features`, `Modules`, `TechStack`, `WhyUs`, `CTA`, `Navbar`).
- Added robust frontend documentation suite (`docs/frontend/`).

### Changed
- Migrated global styles to Tailwind v4 `@theme` block.
- Redesigned motion system to eliminate layout shifts and tone down ambient animations (Restraint over Spectacle).
- Converted `frontend/` from a git submodule to a standard directory within the monorepo.

### Fixed
- Fixed ESLint Fast Refresh (`react-refresh/only-export-components`) violations in providers and UI components.
- Fixed TypeScript `any` types and `Variants` inference issues.
- Fixed missing `cn` imports in simulator components.
- Fixed residual `next-themes` imports in `shadcn/ui` Sonner component.
