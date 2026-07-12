# Design System

## Philosophy
The RL-ERP design system is built to feel premium, calm, and highly professional. It draws inspiration from Apple, Linear, and Vercel. 
- **Landing Page**: Emphasizes cinematic aesthetics, rich glassmorphism, and deep dark-mode contrast to impress in demos and hackathons.
- **Authenticated ERP**: Prioritizes information density, legibility, and high-productivity workflows without distracting elements.

## Tailwind v4 Architecture
We utilize Tailwind CSS v4's modern `@theme` block inside `src/styles/globals.css`. There is no `tailwind.config.js`.

### Color Space
All semantic colors are defined using the `oklch()` color space to ensure perceptually uniform lightness across different hues, making dark mode transitions flawless.

**Semantic Tokens:**
- `--color-background`
- `--color-foreground`
- `--color-card` / `--color-card-foreground`
- `--color-primary` (Our signature accent color)
- `--color-muted`
- `--color-border`
- Success / Warning / Destructive

## Glassmorphism & Utilities
We enforce consistency through reusable utility classes rather than inline arbitrary values:
- `.glass-card`: Standard translucent card with a subtle border.
- `.landing-border-glow`: An animated pseudo-element that creates a slow, rotating gradient border.
- `.premium-blur`: Standardized backdrop filtering for floating elements (navbars, tooltips).

## Typography
- **Headings (Landing)**: Premium serif fonts (e.g., Instrument Serif, Newsreader) for hero sections and dramatic impact.
- **Body & App (ERP)**: Clean sans-serif (e.g., Inter, Geist) for maximum legibility in dense data tables and forms.
