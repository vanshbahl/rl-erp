# Frontend Development Log

## 2026-07-12
### Major Decisions & Architecture Setup
- **Framework Setup**: Initialized React 19 via Vite with the React Compiler (`@rolldown/plugin-babel`) enabled for automatic memoization.
- **Styling Architecture**: Migrated to Tailwind CSS v4, utilizing the new `@theme` configuration inside `globals.css` instead of a separate config file. Standardized on `oklch` for semantic colors.
- **Theme Provider**: Explicitly rejected `next-themes`. Built a custom `ThemeProvider` utilizing the native `document.startViewTransition` API to create a cinematic, circular wipe effect originating from the user's cursor when toggling light/dark mode.

### Implementation: Premium Landing Page
- Structured the landing page into a modular architecture (`src/pages/public/sections/`).
- **Animations Added**: Developed custom, GPU-accelerated Framer Motion primitives: `AuroraBackground`, `Spotlight`, `Magnet`, and a Canvas-based `Noise` generator throttled to 6 FPS for performance.
- **Simulators Built**: 
  - `DashboardSimulator`: A complex, timeline-driven simulation of a manufacturing dashboard updating in real-time (Inventory -> Production -> Sales -> Revenue).
  - `WorkflowVisualization`: An animated SVG graph mapping a supply chain network.

### Motion Philosophy Audit & Redesign
- Conducted a strict motion audit. Decided the initial animations were too chaotic and "floaty".
- **Refinements**: 
  - Completely stripped `scale`, `x`, and `y` animations from landing page scroll reveals.
  - Eliminated all layout shifts (e.g., replaced `height` animations with pure `opacity` crossfades in the DashboardSimulator).
  - Slowed the Aurora background from 30s to 120s and slashed its opacity.
  - Tightened the `Magnet` physics to restrict movement to just a few pixels, achieving a "solid" premium feel akin to Apple and Linear.

### Bug Fixes
- **Git Submodule Issue**: The `frontend/` directory was initially initialized as a git submodule incorrectly. Fixed by removing the gitlink and integrating it into the main RL-ERP repository.
- **Eslint Errors**: Fixed `react-refresh/only-export-components` violations by disabling the rule in specific utility and provider files rather than over-engineering the file splits.
- **Dependency Issues**: Removed residual `next-themes` imports from `shadcn/ui` components (like Sonner).
- **TypeScript Errors**: Resolved generic `any` types and strict `Variants` checking for Framer Motion. 

*Result: The frontend compiles perfectly (`npm run dev`, `npm run lint`, `npm run build` all pass).*
