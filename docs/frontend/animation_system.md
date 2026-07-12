# Animation & Motion System

## Philosophy
RL-ERP uses a strict "Restraint over Spectacle" motion philosophy. The goal is to maximize perceived quality by eliminating layout shifts and chaotic movement. The interface should feel expensive, calm, confident, and deliberate. 

**Core Rules:**
1. **Zero Layout Shifts**: Never animate `height`, `width`, or margins if it pushes other content around.
2. **Pre-rendered Entrances**: All scroll entrances must trigger before entering the viewport (`margin: "100px"`) to prevent cheap pop-in effects.
3. **Pure Fade / Blur**: Avoid translating (`y` or `x`) elements into view. Use `opacity` crossfades, occasionally paired with a subtle `blur` resolve.
4. **Tight Physics**: Spring animations (like magnetic buttons) must use high stiffness (300+) and damping (30+) so they feel solid, not floaty.

## Theme Transitions
Dark/Light mode toggles do not simply crossfade. We intercept the theme toggle and use the native `document.startViewTransition` API to create a cinematic, circular wipe originating from the user's click coordinate.

## Primitives (`src/components/animations/`)
- **AuroraBackground**: A very slow (120s+ duration), low-opacity gradient blob system using `oklch` colors.
- **Noise**: A canvas-based film grain overlay throttled to 6 FPS to add texture without draining the CPU.
- **Spotlight**: A static, heavily blurred radial gradient to simulate subtle lighting.
- **Magnet**: A wrapper component that gently pulls its children (2-3px maximum) toward the cursor to afford interactivity on primary CTAs.
