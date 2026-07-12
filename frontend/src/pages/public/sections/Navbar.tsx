import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { motion, useScroll, useMotionValueEvent } from "motion/react"
import { Sun, Moon, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/app/ThemeProvider"

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Modules", href: "#modules" },
  { label: "Stack", href: "#stack" },
  { label: "Why RL-ERP", href: "#why" },
]

export function Navbar() {
  const { theme, setTheme } = useTheme()
  const { scrollY } = useScroll()
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeSection, setActiveSection] = useState("")

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50)
  })

  // Basic scrollspy
  useEffect(() => {
    const handleScroll = () => {
      const sections = NAV_LINKS.map(l => l.href.substring(1))
      for (const section of sections) {
        const el = document.getElementById(section)
        if (el) {
          const rect = el.getBoundingClientRect()
          if (rect.top <= 200 && rect.bottom >= 200) {
            setActiveSection(section)
            return
          }
        }
      }
      setActiveSection("")
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 px-6 py-4 transition-all duration-300"
    >
      <div className="mx-auto max-w-6xl">
        <div 
          className={`flex items-center justify-between rounded-2xl px-6 py-3 transition-all duration-500 ${
            isScrolled 
              ? "landing-border-glow shadow-lg" 
              : "bg-transparent"
          }`}
        >
          <span className="text-lg font-serif font-semibold tracking-tight">RL-ERP</span>
          
          <div className="hidden items-center gap-1 md:flex">
            {NAV_LINKS.map((link) => {
              const isActive = activeSection === link.href.substring(1)
              return (
                <a
                  key={link.href}
                  href={link.href}
                  className="relative px-4 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  {isActive && (
                    <motion.div
                      layoutId="nav-active"
                      className="absolute inset-0 rounded-full bg-foreground/5 dark:bg-foreground/10"
                      transition={{ type: "spring", stiffness: 500, damping: 40 }}
                    />
                  )}
                  <span className="relative z-10">{link.label}</span>
                </a>
              )
            })}
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={(e) => setTheme(theme === "dark" ? "light" : "dark", e)}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-card/50 border border-border/50 text-muted-foreground transition-all hover:bg-card hover:text-foreground hover:scale-105 active:scale-95"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>
            <Link to="/app/dashboard">
              <Button size="sm" className="gap-2 rounded-xl bg-foreground text-background hover:bg-foreground/90 transition-transform active:scale-95 shadow-[0_0_15px_rgba(255,255,255,0.1)] dark:shadow-[0_0_15px_rgba(0,0,0,0.3)]">
                Open App
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
