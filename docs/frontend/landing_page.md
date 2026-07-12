# Landing Page

The landing page (`src/pages/public/LandingPage.tsx`) serves as the primary marketing vehicle for the RL-ERP project. It is designed to be cinematic, performant, and deeply impressive for hackathons and demos.

## Architecture
To prevent a massive monolithic file, the landing page is broken down into distinct sections located in `src/pages/public/sections/`:
- `Navbar.tsx`
- `Hero.tsx`
- `Features.tsx`
- `Modules.tsx`
- `TechStack.tsx`
- `WhyUs.tsx`
- `CTA.tsx`

## Design Philosophy
The page follows a strict "Restraint over Spectacle" aesthetic inspired by Apple, Linear, and Vercel. 
- Deep dark mode contrasts with subtle OKLCH primary accents.
- All scroll entrances are pure opacity fades or subtle blurs, triggering *before* entering the viewport to eliminate pop-in.
- Background animations (Aurora, Spotlight) are heavily throttled and reduced in opacity to act as calm ambience rather than distracting elements.
- The `DashboardSimulator` serves as the emotional centerpiece, proving the software's capability without requiring a user to log in.
