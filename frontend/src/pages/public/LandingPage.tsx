import { Navbar } from "./sections/Navbar"
import { Hero } from "./sections/Hero"
import { Features } from "./sections/Features"
import { Modules } from "./sections/Modules"
import { TechStack } from "./sections/TechStack"
import { WhyUs } from "./sections/WhyUs"
import { CTA } from "./sections/CTA"

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-background text-foreground transition-colors duration-500">
      <Navbar />
      
      <main>
        <Hero />
        <Features />
        <Modules />
        <TechStack />
        <WhyUs />
        <CTA />
      </main>

      <footer className="border-t border-border/20 px-6 py-12 relative z-10 bg-background">
        <div className="mx-auto flex max-w-6xl flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg font-serif font-semibold tracking-tight">RL-ERP</span>
            <span className="text-sm text-muted-foreground">
              © {new Date().getFullYear()}
            </span>
          </div>
          <span className="text-xs text-muted-foreground/60">
            Built with React, FastAPI & PostgreSQL
          </span>
        </div>
      </footer>
    </div>
  )
}
