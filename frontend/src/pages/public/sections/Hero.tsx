import { useRef } from "react"
import { motion, useScroll, useTransform } from "motion/react"
import { Link } from "react-router-dom"
import { ArrowRight, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AuroraBackground } from "@/components/animations/AuroraBackground"
import { Noise } from "@/components/animations/Noise"
import { Spotlight } from "@/components/animations/Spotlight"
import { Magnet } from "@/components/animations/Magnet"
import { DashboardSimulator } from "@/components/simulations/DashboardSimulator"

export function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-start overflow-hidden pt-32 pb-20">
      <AuroraBackground />
      <Noise />
      <Spotlight />

      <div className="relative z-10 flex w-full max-w-6xl flex-col items-center px-6">
        <div
          className="flex flex-col items-center text-center"
        >
          <motion.div
            initial={{ opacity: 0, filter: "blur(4px)" }}
            animate={{ opacity: 1, filter: "blur(0px)" }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <Badge
              variant="secondary"
              className="mb-8 gap-1.5 rounded-full border-border/50 bg-background/50 px-4 py-1.5 text-xs backdrop-blur-md"
            >
              <Sparkles className="h-3 w-3 text-primary" />
              Open-Source ERP Platform
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto max-w-4xl font-serif text-5xl leading-[1.1] tracking-tight sm:text-6xl md:text-7xl lg:text-8xl"
          >
            <span className="landing-gradient-text">Enterprise Resource</span>
            <br />
            <span className="text-foreground">Planning,</span>{" "}
            <span className="landing-gradient-text italic">Reimagined</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg"
          >
            A modern, modular ERP built with the technologies your team already loves.
            Fast, beautiful, and ready to scale.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="mt-10 flex flex-wrap items-center justify-center gap-4"
          >
            <Magnet padding={50}>
              <Link to="/app/dashboard">
                <Button size="lg" className="group h-12 gap-2 rounded-xl bg-primary px-8 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                  Start Building
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            </Magnet>
          </motion.div>
        </div>

        {/* Dashboard Simulator */}
        <motion.div
          initial={{ opacity: 0, filter: "blur(10px)" }}
          animate={{ opacity: 1, filter: "blur(0px)" }}
          transition={{ duration: 1.2, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="mt-20 w-full max-w-5xl [perspective:1000px]"
        >
          <DashboardSimulator />
        </motion.div>
      </div>
      
      {/* Fade out bottom edge of hero */}
      <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent z-10" />
    </section>
  )
}
