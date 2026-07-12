import { useRef } from "react"
import { motion, useInView } from "motion/react"
import { Badge } from "@/components/ui/badge"

const STACK_ITEMS = [
  { label: "React 19", desc: "UI Framework" },
  { label: "FastAPI", desc: "Backend API" },
  { label: "PostgreSQL", desc: "Database" },
  { label: "TypeScript", desc: "Type Safety" },
  { label: "Tailwind CSS v4", desc: "Styling" },
  { label: "TanStack Query", desc: "Data Fetching" },
  { label: "SQLAlchemy 2", desc: "ORM" },
  { label: "Zustand", desc: "State Management" },
]

export function TechStack() {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: "100px" })

  return (
    <section id="stack" className="px-6 py-32 overflow-hidden">
      <div className="mx-auto max-w-6xl relative">
        
        {/* Decorative background flare */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[300px] bg-primary/5 blur-[120px] rounded-full pointer-events-none" />

        <motion.div 
          ref={ref}
          className="text-center relative z-10"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <Badge variant="secondary" className="mb-4 rounded-full px-3 py-1 text-xs bg-background/80 backdrop-blur-md">
            Technology
          </Badge>
          <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
            Powered by <span className="landing-gradient-text italic">modern technology</span>
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
            Batteries included. No legacy baggage.
          </p>
        </motion.div>

        <div className="mt-20 relative z-10">
          <div className="landing-border-glow grid grid-cols-2 sm:grid-cols-4 overflow-hidden rounded-3xl bg-background/50 backdrop-blur-xl">
            {STACK_ITEMS.map((item, i) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true, margin: "100px" }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
                className="group relative flex flex-col items-center justify-center p-8 text-center transition-colors hover:bg-card/40 border-b border-r border-border/30 last:border-r-0 sm:[&:nth-child(4n)]:border-r-0 [&:nth-last-child(-n+4)]:border-b-0"
              >
                {/* Hover gradient glow */}
                <div className="absolute inset-0 opacity-0 bg-gradient-to-br from-primary/10 to-transparent transition-opacity duration-500 group-hover:opacity-100" />
                
                <span className="relative z-10 text-base font-semibold">{item.label}</span>
                <span className="relative z-10 mt-1 text-xs text-muted-foreground transition-colors group-hover:text-primary">
                  {item.desc}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
