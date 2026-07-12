# Components

## Radix UI & shadcn/ui
The base component library is built on `shadcn/ui`, which provides unstyled, accessible Radix UI primitives wrapped in Tailwind CSS. 
These components are located in `src/components/ui/` and are fully owned by the codebase (not imported as an npm package), allowing complete customization of the design system.

## Motion Primitives
Custom Framer Motion primitives are located in `src/components/animations/`:
- `AuroraBackground.tsx`
- `Magnet.tsx`
- `Noise.tsx`
- `Spotlight.tsx`

## Simulations
High-fidelity React components built specifically to demonstrate ERP capabilities on the Landing Page. Located in `src/components/simulations/`:
- `DashboardSimulator.tsx`: A timeline-driven, interactive simulation of a manufacturing ERP dashboard with live charts and activity feeds.
- `WorkflowVisualization.tsx`: An animated SVG network mapping the supply chain from Supplier to Customer.
