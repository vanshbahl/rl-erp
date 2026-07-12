import { useRef } from "react"
import { motion, useScroll, useTransform, useInView } from "motion/react"
import { Shield, Zap, Globe, Layers } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const FEATURES = [
  {
    icon: Zap,
    title: "Lightning Fast",
    desc: "Sub-100ms interactions. React Compiler + code-splitting deliver enterprise performance.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    desc: "JWT authentication, role-based access control, and audit logging built in.",
  },
  {
    icon: Globe,
    title: "API-First",
    desc: "FastAPI backend with auto-generated OpenAPI docs. Every feature is an API.",
  },
  {
    icon: Layers,
    title: "Modular Architecture",
    desc: "Feature-sliced design lets you enable only the modules your business needs.",
  },
]

export function Features() {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: "100px" })
  
  return (
    <section id="features" className="relative px-6 py-32 overflow-hidden">
      <div className="mx-auto max-w-6xl">
        <motion.div 
          ref={ref}
          className="text-center"
          initial={{ opacity: 0, filter: "blur(10px)" }}
          animate={isInView ? { opacity: 1, filter: "blur(0px)" } : {}}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <Badge variant="secondary" className="mb-4 rounded-full px-3 py-1 text-xs">
            Architecture
          </Badge>
          <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
            Built for <span className="landing-gradient-text italic">performance</span>
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
            Every architectural decision optimized for speed, security, and developer productivity.
          </p>
        </motion.div>

        <div className="mt-20 grid gap-6 sm:grid-cols-2">
          {FEATURES.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, filter: "blur(4px)" }}
              whileInView={{ opacity: 1, filter: "blur(0px)" }}
              viewport={{ once: true, margin: "100px" }}
              transition={{ duration: 0.8, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
            >
              <Card className="glass-card overflow-hidden transition-all duration-300 hover:border-primary/50 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] group">
                <CardContent className="p-8">
                  <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">{feature.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                    {feature.desc}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
