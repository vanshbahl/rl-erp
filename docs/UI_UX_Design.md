# UI/UX Design Guidelines

## 1. Design Philosophy

RL-ERP is internal industrial operations software for Raman Laaminators. The authenticated application prioritizes operational clarity, information density, reliability, and professional restraint.

- Light theme is the primary and default experience.
- Surface tone, spacing, typography, and subtle borders communicate hierarchy.
- Color communicates action, status, priority, and exceptions.
- The ERP must not use marketing heroes, glassmorphism, gradients, floating cards, or decorative dashboard treatments.
- Animations are limited to useful interface feedback and existing component transitions.

The public landing page may retain its separate marketing presentation. These ERP rules govern authenticated and authentication interfaces.

## 2. Color and Surfaces

- Main background: soft neutral gray around `#F6F6F4`.
- Sidebar: quiet warm gray around `#F2F2F0`; top bar, cards, dialogs, and data surfaces: white or near-white.
- Primary text: softened near-black around `#252525`.
- Secondary and muted text: readable neutral grays without excessive contrast.
- Standard borders: approximately `#E1E1DE`; subtle separators: approximately `#E8E8E5`.
- Primary action and active navigation: restrained blue.
- Success: green; warning: amber; destructive/error: red; inactive/draft: gray.

Dark-mode infrastructure may remain available, but features must be designed and verified in light mode first.

## 3. Geometry

Use restrained rounding to soften the interface without turning it into a pill-based SaaS design:

- Major cards and panels: 6–10px
- Inputs, buttons, menus, and navigation states: 4–6px
- Dense tables and operational surfaces: 0–4px where practical
- Status badges: approximately 4px; pills only when status readability benefits

Avoid large 16–24px radii. Circular geometry is reserved for inherently circular controls such as avatars, status dots, radio buttons, and icon indicators.

## 4. Typography and Density

Use the existing Inter/system sans-serif stack.

- Page title: 22–24px, semibold
- Section title: 15–17px, semibold
- Body and primary UI: 13–14px
- Metadata: 12px
- Table heading: 11–12px, medium or semibold

Tables and financial values use tabular numerals. Prefer compact spacing, 38–42px form controls, compact table rows, and consistent 1px separators. Avoid oversized headings, excessive padding, and large empty dashboard areas.

## 5. Application Shell

- Desktop uses a persistent 224px sidebar, 64px search/utility bar, 48px page-context bar, and scrollable content area.
- Sidebar navigation is grouped by business area. The active route uses a restrained light-blue state with a thin blue left border.
- Routes that are not implemented are visually disabled and must not navigate to fake screens.
- User identity, role, and logout remain directly accessible in the sidebar footer.
- The top bar gives the existing command search meaningful width and keeps current user identity compact at the right.
- The context bar identifies the current page and supplies concise date context.
- Mobile replaces the persistent sidebar with a full-height navigation sheet and keeps logout available.

## 6. Page Pattern

Authenticated pages follow this structure:

1. Page title and short operational description
2. Optional primary action
3. Search and filters when relevant
4. Main table, form, or operational content

Use the shared `PageHeader` and `EmptyState` patterns where appropriate. Do not add decorative hero sections inside the ERP.

## 7. Components

- Buttons: compact, 4–6px radius, clear primary/secondary/destructive hierarchy.
- Inputs/selects: restrained radius, visible border, accessible label, clear blue focus state.
- Cards/panels: 6–10px radius, very light border, no floating shadow by default.
- Tables: full width, soft neutral header background, compact rows, subtle separators, gentle hover state, and horizontal scrolling when necessary.
- Badges: small-radius, restrained semantic colors, uppercase compact labels.
- Dialogs are softly rounded; edge-docked sheets remain crisp, bordered, white, compact, and mobile-safe.
- Tooltips, dropdowns, popovers, and command surfaces use an off-white background, light border, dark-gray text, and a very subtle floating shadow. Dark default tooltips are not used in the light interface.
- Empty states: concise text and only real, available actions. Never show “Connect API” controls.
- Loading: skeleton rows or blocks that preserve layout; full-screen loading is reserved for initial authentication restoration.
- Errors: concise user-safe messages; do not expose raw API payloads.

## 8. Responsive Behavior

- Verify practical widths around 360px, 390px, 430px, and 768px.
- Dashboard summaries use an asymmetric desktop grid and selective one/two-column mobile composition.
- Dashboard panels stack into one column below desktop widths.
- Dense tables may scroll horizontally; future modules may use mobile record cards when that better preserves meaning.
- Pages must not cause unnecessary viewport overflow.

## 9. Accessibility

- Text and controls must meet WCAG AA contrast.
- All actions must be keyboard reachable with visible focus states.
- Icon-only buttons require accessible labels.
- Disabled future navigation must be identifiable as unavailable and must not behave like a link.
- Loading, empty, error, and status states must not rely on color alone.
