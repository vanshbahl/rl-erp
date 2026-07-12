import { Link } from "react-router-dom"
import { motion } from "motion/react"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Magnet } from "@/components/animations/Magnet"

export function CTA() {
  return (
    <section className="px-6 py-32 relative overflow-hidden">
      {/* Background glow specific to CTA */}
      <div className="absolute bottom-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-primary/20 blur-[150px] rounded-full pointer-events-none" />

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: "100px" }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="mx-auto max-w-3xl text-center relative z-10">
          <div className="landing-border-glow rounded-3xl p-12 sm:p-20 shadow-2xl relative overflow-hidden">
            {/* Subtle inner grid/noise or lighting could go here */}
            <div className="absolute inset-0 bg-gradient-to-b from-card/10 to-card/50 pointer-events-none" />
            
            <h2 className="relative z-10 font-serif text-4xl tracking-tight sm:text-5xl md:text-6xl">
              Ready to <span className="landing-gradient-text italic">get started</span>?
            </h2>
            <p className="relative z-10 mx-auto mt-6 max-w-md text-lg text-muted-foreground">
              Deploy RL-ERP on your own infrastructure and take control of your business operations.
            </p>
            
            <div className="relative z-10 mt-10 flex flex-wrap items-center justify-center gap-4">
              <Magnet padding={60}>
                <Link to="/app/dashboard">
                  <Button size="lg" className="group h-14 gap-2 rounded-xl bg-primary px-10 text-base font-medium text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(var(--color-primary),0.3)]">
                    Launch Dashboard
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Button>
                </Link>
              </Magnet>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  )
}
