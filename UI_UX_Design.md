# UI/UX Design Guidelines

## 1. Design Philosophy
The RL-ERP interface is designed to break away from traditional, sterile corporate software. It emphasizes **Premium Utility**. The interface must look stunning, feel incredibly fast, and prioritize heavy data-density without feeling cluttered. 
- **Clarity Over Cleverness:** Data and actions must be immediately obvious.
- **Dynamic & Alive:** Interactions should feel responsive. Use subtle micro-animations to acknowledge user input.
- **Dark-Mode First (But Flexible):** The system heavily leans into modern, high-contrast dark themes utilizing glassmorphism and subtle gradients, but must fully support a pristine light mode.

## 2. Visual Identity & Color System
The color palette avoids basic primaries (pure red, green, blue) in favor of tailored, harmonious HSL values.

- **Backgrounds (Dark):** Deep, rich off-blacks (e.g., `hsl(220, 10%, 10%)`). Never `#000000`.
- **Backgrounds (Light):** Soft, cool off-whites (e.g., `hsl(220, 20%, 98%)`).
- **Primary Accent:** An electric, vibrant accent (e.g., Indigo/Violet gradient) used sparingly for primary actions (Submit buttons, active sidebar states).
- **Secondary Accent:** Muted slate or zinc for secondary actions and borders.
- **Semantic Colors:**
  - **Success:** Emerald/Teal blends (used for `COMPLETED` statuses).
  - **Warning:** Amber/Orange blends (used for `LOW_STOCK` or `PENDING`).
  - **Danger:** Rose/Crimson blends (used for `CANCELLED` or destructive actions).
  - **Info:** Sky/Blue blends (used for `IN_PROGRESS`).

## 3. Typography
- **Primary Font:** `Inter` or `Geist` (Google Fonts/Vite integration). Sans-serif, highly legible at small sizes.
- **Data/Numbers Font:** Use tabular lining (`font-variant-numeric: tabular-nums`) for all tables, invoices, and financial data to ensure vertical alignment of digits.
- **Hierarchy:**
  - Page Titles (H1): 24px - 32px, Semibold, tight tracking.
  - Section Headers (H2/H3): 16px - 20px, Medium.
  - Body Text: 14px, Regular, 1.5 line height.
  - Meta/Small Text: 12px, Medium, muted color.

## 4. Spacing & Layout
- **Grid System:** Standard 8px scale (8, 16, 24, 32, 48, 64).
- **Application Shell:**
  - Fixed left Sidebar (collapsible) containing main navigation.
  - Fixed top Navbar for global search, user profile, and breadcrumbs.
  - Main content area with a max-width wrapper (e.g., `max-w-7xl`) for readability on ultra-wide monitors.
- **Card Layouts:** Use subtle borders (`border-border`) and soft shadows for cards. In dark mode, rely on surface color elevation (lighter backgrounds) rather than heavy drop shadows.

## 5. Components & Shadcn UI
The project utilizes Tailwind CSS v4 and Shadcn UI. Do not write custom CSS for basic components.
- **Buttons:** Slight border-radius (`rounded-md` or `rounded-lg`). Primary buttons have subtle hover glow effects.
- **Inputs/Selects:** Subdued borders, clearly defined focus states (`ring-2 ring-primary/50`).
- **Badges:** Pill-shaped, used extensively for rendering status indicators (e.g., Order Status, Product Type).
- **Tables:** 
  - Sticky headers.
  - Hover states on rows.
  - Right-aligned columns for all numeric/currency data.
  - Left-aligned columns for text/IDs.

## 6. Interaction & Animation
Utilize Framer Motion for restraint-focused animations.
- **Page Transitions:** Subtle fade and slide-up (e.g., `y: 10, opacity: 0` to `y: 0, opacity: 1`, duration: 0.2s).
- **Modals/Dialogs:** Scale-in effect (`scale: 0.95`).
- **Hover Effects:** Micro-transformations on interactive cards (e.g., `hover:-translate-y-0.5`).
- **Loading States:** 
  - Prefer Skeleton loaders over generic spinning wheels for data-heavy views.
  - Skeletons should roughly match the shape of the data being loaded.

## 7. UX Principles
- **Destructive Actions:** Deleting records or rolling back production runs *must* require confirmation via a dialog or double-click mechanism.
- **Forms:** 
  - Group related fields logically.
  - Use clear helper text below ambiguous inputs.
  - Disable submit buttons during pending network requests to prevent duplicate submissions.
- **Empty States:** When a table is empty (e.g., "No orders found"), display a centralized, friendly graphic/icon with a clear Call-To-Action (CTA) to create the first record.
- **Toasts:** Use unobtrusive, bottom-right toast notifications for success/error API responses. Never use blocking `alert()` popups.

## 8. Accessibility (a11y)
- **Contrast:** Ensure all text passes WCAG AA contrast ratios against its background.
- **Keyboard Navigation:** All interactive elements must be reachable via `Tab` and have visible focus states.
- **Screen Readers:** Use `aria-label` on icon-only buttons (like edit/delete actions in tables).
