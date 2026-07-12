import { motion, useReducedMotion } from "motion/react"
import { useTheme } from "@/app/ThemeProvider"
import { cn } from "@/lib/utils"

export function AuroraBackground({ className }: { className?: string }) {
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const prefersReducedMotion = useReducedMotion()

  // Base gradients
  const bg = isDark
    ? "oklch(0.13 0.01 260)"
    : "oklch(0.98 0.005 260)"
  const aura1 = isDark
    ? "oklch(0.62 0.15 250 / 0.05)"
    : "oklch(0.55 0.18 250 / 0.05)"
  const aura2 = isDark
    ? "oklch(0.72 0.12 200 / 0.03)"
    : "oklch(0.40 0.12 200 / 0.03)"
  const aura3 = isDark
    ? "oklch(0.62 0.15 250 / 0.03)"
    : "oklch(0.60 0.15 250 / 0.03)"

  return (
    <div
      className={cn(
        "absolute inset-0 z-0 overflow-hidden pointer-events-none transition-colors duration-1000",
        className
      )}
      style={{ backgroundColor: bg }}
    >
      <motion.div
        animate={
          prefersReducedMotion
            ? { opacity: 1 }
            : {
                rotate: [0, 10, -10, 0],
              }
        }
        transition={{
          repeat: Infinity,
          repeatType: "mirror",
          duration: 120,
          ease: "linear",
        }}
        className="absolute top-[-20%] left-[10%] h-[120vh] w-[120vh] rounded-full mix-blend-screen filter blur-[120px]"
        style={{
          background: `radial-gradient(circle at 50% 50%, ${aura1} 0%, transparent 60%)`,
        }}
      />
      <motion.div
        animate={
          prefersReducedMotion
            ? { opacity: 1 }
            : {
                rotate: [0, -15, 10, 0],
              }
        }
        transition={{
          repeat: Infinity,
          repeatType: "mirror",
          duration: 140,
          ease: "linear",
        }}
        className="absolute top-[10%] right-[-10%] h-[100vh] w-[100vh] rounded-full mix-blend-screen filter blur-[100px]"
        style={{
          background: `radial-gradient(circle at 50% 50%, ${aura2} 0%, transparent 60%)`,
        }}
      />
      <motion.div
        animate={
          prefersReducedMotion
            ? { opacity: 1 }
            : {
                rotate: [0, 5, -5, 0],
                x: [0, 50, -50, 0],
              }
        }
        transition={{
          repeat: Infinity,
          repeatType: "mirror",
          duration: 130,
          ease: "linear",
        }}
        className="absolute bottom-[-20%] left-[30%] h-[110vh] w-[110vh] rounded-full mix-blend-screen filter blur-[110px]"
        style={{
          background: `radial-gradient(circle at 50% 50%, ${aura3} 0%, transparent 60%)`,
        }}
      />
    </div>
  )
}
