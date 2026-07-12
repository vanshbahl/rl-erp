import { motion } from "motion/react"
import { CheckCircle2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"

const WHY_ITEMS = [
  {
    title: "Built for Growing Businesses",
    desc: "Start with the modules you need today, activate more as you grow. No enterprise license fees.",
  },
  {
    title: "Modern Developer Experience",
    desc: "TypeScript end-to-end, auto-generated API clients, hot reloading, and instant feedback loops.",
  },
  {
    title: "Self-Hosted & Private",
    desc: "Your data stays on your infrastructure. No vendor lock-in, no surprise pricing changes.",
  },
  {
    title: "Hackathon-Proven",
    desc: "Designed to be demo-ready in hours, production-ready in weeks. Move fast without breaking things.",
  },
]

export function WhyUs() {
  return (
    <section id="why" className="px-6 py-32 bg-card/10">
      <div className="mx-auto max-w-6xl">
        <motion.div 
          className="text-center mb-20"
          initial={{ opacity: 0, filter: "blur(4px)" }}
          whileInView={{ opacity: 1, filter: "blur(0px)" }}
          viewport={{ once: true, margin: "100px" }}
          transition={{ duration: 0.6 }}
        >
          <Badge variant="secondary" className="mb-4 rounded-full px-3 py-1 text-xs">
            Why RL-ERP
          </Badge>
          <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
            Not another <span className="landing-gradient-text italic">bloated ERP</span>
          </h2>
        </motion.div>

        <div className="grid gap-6 sm:grid-cols-2">
          {WHY_ITEMS.map((item, i) => (
            <motion.div 
              key={item.title}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, margin: "100px" }}
              transition={{ duration: 0.7, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="flex gap-5 rounded-2xl border border-border/20 bg-background/50 p-8 backdrop-blur-sm transition-all hover:bg-card/40 hover:border-primary/20">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-success/10">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{item.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {item.desc}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
