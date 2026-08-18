# UI/UX Design Guidelines

## 1. Design Philosophy

RL-ERP is internal industrial operations software for Raman Laaminators. The authenticated application prioritizes operational clarity, information density, reliability, and professional restraint.

- Light theme is the primary and default experience.
- Structure and visible borders communicate hierarchy.
- Color communicates action, status, priority, and exceptions.
- The ERP must not use marketing heroes, glassmorphism, gradients, floating cards, or decorative dashboard treatments.
- Animations are limited to useful interface feedback and existing component transitions.

The public landing page may retain its separate marketing presentation. These ERP rules govern authenticated and authentication interfaces.

## 2. Color and Surfaces

- Main background: very light neutral gray.
- Sidebar, top bar, cards, dialogs, and data surfaces: white or near-white.
- Primary text: near-black neutral.
- Secondary text: readable neutral gray.
- Borders and inputs: visible neutral gray.
- Primary action and active navigation: restrained blue.
- Success: green; warning: amber; destructive/error: red; inactive/draft: gray.

Dark-mode infrastructure may remain available, but features must be designed and verified in light mode first.

## 3. Geometry

ERP components use square corners (`border-radius: 0`) consistently:

- Buttons and inputs
- Cards and panels
- Tables and filters
- Navigation states
- Badges
- Dropdowns and popovers
- Dialogs and sheets
- Skeleton and empty-state surfaces

Circular geometry is reserved for inherently circular controls such as avatars, status dots, radio buttons, and icon indicators.

## 4. Typography and Density

Use the existing Inter/system sans-serif stack.

- Page title: 22–24px, semibold
- Section title: 15–17px, semibold
- Body and primary UI: 13–14px
- Metadata: 12px
- Table heading: 11–12px, medium or semibold

Tables and financial values use tabular numerals. Prefer compact spacing, 38–42px form controls, compact table rows, and consistent 1px separators. Avoid oversized headings, excessive padding, and large empty dashboard areas.

## 5. Application Shell

- Desktop uses a persistent 232px sidebar, compact 56px top bar, and scrollable content area.
- Sidebar navigation is grouped by business area. The active route uses a square light-blue state with a strong blue left border.
- Routes that are not implemented are visually disabled and must not navigate to fake screens.
- User identity, role, and logout remain directly accessible in the sidebar footer.
- The top bar contains page context, existing command search access, and current user identity.
- Mobile replaces the persistent sidebar with a full-height navigation sheet and keeps logout available.

## 6. Page Pattern

Authenticated pages follow this structure:

1. Page title and short operational description
2. Optional primary action
3. Search and filters when relevant
4. Main table, form, or operational content

Use the shared `PageHeader` and `EmptyState` patterns where appropriate. Do not add decorative hero sections inside the ERP.

## 7. Components

- Buttons: square, compact, clear primary/secondary/destructive hierarchy.
- Inputs/selects: square, visible border, accessible label, clear focus ring.
- Cards/panels: square, 1px border, no floating shadow by default.
- Tables: full width, subtle header background, compact rows, horizontal separators, hover state, and horizontal scrolling when necessary.
- Badges: square, restrained semantic colors, uppercase compact labels.
- Dialogs/sheets: square, bordered, white, compact, and mobile-safe.
- Empty states: concise text and only real, available actions. Never show “Connect API” controls.
- Loading: skeleton rows or blocks that preserve layout; full-screen loading is reserved for initial authentication restoration.
- Errors: concise user-safe messages; do not expose raw API payloads.

## 8. Responsive Behavior

- Verify practical widths around 360px, 390px, 430px, and 768px.
- KPI layouts use four columns on desktop, two where readable on small screens, and one when necessary.
- Dashboard panels stack into one column below desktop widths.
- Dense tables may scroll horizontally; future modules may use mobile record cards when that better preserves meaning.
- Pages must not cause unnecessary viewport overflow.

## 9. Accessibility

- Text and controls must meet WCAG AA contrast.
- All actions must be keyboard reachable with visible focus states.
- Icon-only buttons require accessible labels.
- Disabled future navigation must be identifiable as unavailable and must not behave like a link.
- Loading, empty, error, and status states must not rely on color alone.
