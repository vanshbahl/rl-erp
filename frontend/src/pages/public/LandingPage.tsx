import { useRef } from "react"
import { Link } from "react-router-dom"
import { motion, useInView } from "motion/react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import {
  ArrowRight,
  Package,
  Users,
  ShoppingCart,
  BarChart3,
  FileText,
  Truck,
  Boxes,
  Receipt,
  Settings,
  Shield,
  Zap,
  Globe,
  Layers,
  CheckCircle2,
  Sparkles,
  ChevronRight,
} from "lucide-react"

function AnimatedSection({
  children,
  className = "",
  delay = 0,
}: {
  children: React.ReactNode
  className?: string
  delay?: number
}) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: "-80px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Modules", href: "#modules" },
  { label: "Stack", href: "#stack" },
  { label: "Why RL-ERP", href: "#why" },
]

const MODULES = [
  { icon: Package, label: "Products", desc: "Catalog & variants management" },
  { icon: Users, label: "Customers", desc: "CRM & customer lifecycle" },
  { icon: Truck, label: "Suppliers", desc: "Vendor management & procurement" },
  { icon: ShoppingCart, label: "Sales Orders", desc: "Order-to-cash pipeline" },
  { icon: FileText, label: "Purchase Orders", desc: "Procure-to-pay workflow" },
  { icon: Boxes, label: "Inventory", desc: "Stock tracking & warehouse ops" },
  { icon: Receipt, label: "Invoicing", desc: "Billing & payment tracking" },
  { icon: BarChart3, label: "Reports", desc: "Real-time business analytics" },
  { icon: Settings, label: "Settings", desc: "Roles, preferences & config" },
]

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

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background ambient effects */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div
          className="absolute top-[-20%] left-[10%] h-[600px] w-[600px] rounded-full opacity-[0.07]"
          style={{
            background:
              "radial-gradient(circle, oklch(0.62 0.15 250) 0%, transparent 70%)",
          }}
        />
        <div
          className="absolute top-[30%] right-[-5%] h-[500px] w-[500px] rounded-full opacity-[0.05]"
          style={{
            background:
              "radial-gradient(circle, oklch(0.72 0.12 200) 0%, transparent 70%)",
          }}
        />
        <div
          className="absolute bottom-[-10%] left-[40%] h-[400px] w-[400px] rounded-full opacity-[0.04]"
          style={{
            background:
              "radial-gradient(circle, oklch(0.62 0.15 250) 0%, transparent 70%)",
          }}
        />
      </div>

      <div className="relative z-10">
        {/* ─── Navbar ────────────────────────────────────── */}
        <motion.nav
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="fixed top-0 left-0 right-0 z-50"
        >
          <div className="mx-auto max-w-6xl px-6 py-4">
            <div className="landing-border-glow flex items-center justify-between rounded-2xl px-6 py-3">
              <span className="text-lg font-semibold tracking-tight">RL-ERP</span>
              <div className="hidden items-center gap-8 md:flex">
                {NAV_LINKS.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </a>
                ))}
              </div>
              <Link to="/app/dashboard">
                <Button size="sm" className="gap-2 rounded-xl">
                  Open App
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </div>
        </motion.nav>

        {/* ─── Hero ──────────────────────────────────────── */}
        <section className="relative flex min-h-screen flex-col items-center justify-center px-6 pt-24">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="text-center"
          >
            <Badge
              variant="secondary"
              className="mb-6 gap-1.5 rounded-full border-border/50 px-4 py-1.5 text-xs"
            >
              <Sparkles className="h-3 w-3 text-primary" />
              Open-Source ERP Platform
            </Badge>

            <h1 className="mx-auto max-w-4xl font-serif text-5xl leading-[1.1] tracking-tight sm:text-6xl md:text-7xl lg:text-8xl">
              <span className="landing-gradient-text">Enterprise Resource</span>
              <br />
              <span className="text-foreground">Planning,</span>{" "}
              <span className="landing-gradient-text italic">Reimagined</span>
            </h1>

            <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
              A modern, modular ERP built with the technologies your team already loves.
              Fast, beautiful, and ready to scale.
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              <Link to="/app/dashboard">
                <Button size="lg" className="gap-2 rounded-xl px-6 text-sm">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <a href="#features">
                <Button
                  variant="outline"
                  size="lg"
                  className="gap-2 rounded-xl border-border/50 px-6 text-sm"
                >
                  See Features
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </a>
            </div>
          </motion.div>

          {/* Hero glow line */}
          <motion.div
            initial={{ scaleX: 0, opacity: 0 }}
            animate={{ scaleX: 1, opacity: 1 }}
            transition={{ duration: 1.2, delay: 0.8 }}
            className="mt-16 h-px w-full max-w-2xl"
            style={{
              background:
                "linear-gradient(90deg, transparent, oklch(0.62 0.15 250 / 0.4), oklch(0.72 0.12 200 / 0.3), transparent)",
            }}
          />

          {/* ─── Live Dashboard Preview ──────────────────── */}
          <AnimatedSection className="mt-12 w-full max-w-5xl" delay={0.2}>
            <div className="landing-border-glow overflow-hidden rounded-2xl p-1">
              <div className="rounded-xl bg-card">
                {/* Mock browser bar */}
                <div className="flex items-center gap-2 border-b border-border px-4 py-3">
                  <div className="flex gap-1.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-red-500/30" />
                    <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/30" />
                    <div className="h-2.5 w-2.5 rounded-full bg-green-500/30" />
                  </div>
                  <div className="ml-4 flex-1 rounded-md bg-muted/50 px-3 py-1 text-xs text-muted-foreground">
                    app.rl-erp.com/dashboard
                  </div>
                </div>
                {/* Mock dashboard */}
                <div className="p-6">
                  <div className="grid gap-3 sm:grid-cols-4">
                    {["Revenue", "Orders", "Products", "Customers"].map(
                      (label, i) => (
                        <div
                          key={label}
                          className="rounded-lg border border-border/50 bg-background/50 p-4"
                        >
                          <p className="text-xs text-muted-foreground">{label}</p>
                          <p className="mt-1 text-xl font-semibold tabular-nums">
                            {["$284K", "1,429", "847", "2,156"][i]}
                          </p>
                          <p className="mt-0.5 text-xs text-success">
                            {["+12.5%", "+8.3%", "+24", "+156"][i]}
                          </p>
                        </div>
                      ),
                    )}
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    {/* Chart placeholder bars */}
                    <div className="col-span-2 rounded-lg border border-border/50 bg-background/50 p-4">
                      <p className="mb-3 text-xs font-medium text-muted-foreground">
                        Revenue Trend
                      </p>
                      <div className="flex h-24 items-end gap-1">
                        {[40, 55, 45, 60, 75, 65, 80, 70, 85, 90, 78, 95].map(
                          (h, i) => (
                            <motion.div
                              key={i}
                              initial={{ height: 0 }}
                              whileInView={{ height: `${h}%` }}
                              viewport={{ once: true }}
                              transition={{ duration: 0.4, delay: i * 0.05 }}
                              className="flex-1 rounded-sm bg-primary/60"
                            />
                          ),
                        )}
                      </div>
                    </div>
                    <div className="rounded-lg border border-border/50 bg-background/50 p-4">
                      <p className="mb-3 text-xs font-medium text-muted-foreground">
                        Top Products
                      </p>
                      <div className="space-y-2">
                        {["Widget Pro", "Sensor Kit", "Control Unit"].map(
                          (name, i) => (
                            <div
                              key={name}
                              className="flex items-center justify-between text-xs"
                            >
                              <span className="text-muted-foreground">{name}</span>
                              <span className="tabular-nums font-medium">
                                {[342, 256, 189][i]}
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </AnimatedSection>
        </section>

        {/* ─── Features ──────────────────────────────────── */}
        <section id="features" className="px-6 py-24">
          <div className="mx-auto max-w-6xl">
            <AnimatedSection className="text-center">
              <Badge
                variant="secondary"
                className="mb-4 rounded-full px-3 py-1 text-xs"
              >
                Features
              </Badge>
              <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
                Built for{" "}
                <span className="landing-gradient-text italic">performance</span>
              </h2>
              <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
                Every architectural decision optimized for speed, security, and developer productivity.
              </p>
            </AnimatedSection>

            <div className="mt-16 grid gap-6 sm:grid-cols-2">
              {FEATURES.map((feature, i) => (
                <AnimatedSection key={feature.title} delay={i * 0.1}>
                  <Card className="glass-card border-border/30 transition-colors hover:border-border/60">
                    <CardContent className="p-6">
                      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                        <feature.icon className="h-5 w-5 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold">{feature.title}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                        {feature.desc}
                      </p>
                    </CardContent>
                  </Card>
                </AnimatedSection>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Modules ───────────────────────────────────── */}
        <section id="modules" className="px-6 py-24">
          <div className="mx-auto max-w-6xl">
            <AnimatedSection className="text-center">
              <Badge
                variant="secondary"
                className="mb-4 rounded-full px-3 py-1 text-xs"
              >
                Modules
              </Badge>
              <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
                Everything your business{" "}
                <span className="landing-gradient-text italic">needs</span>
              </h2>
              <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
                Modular by design. Activate what you need, when you need it.
              </p>
            </AnimatedSection>

            <div className="mt-16 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {MODULES.map((mod, i) => (
                <AnimatedSection key={mod.label} delay={i * 0.06}>
                  <div className="group flex items-start gap-4 rounded-xl border border-border/30 bg-card/30 p-5 transition-all hover:border-border/60 hover:bg-card/60">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/15">
                      <mod.icon className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold">{mod.label}</h3>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {mod.desc}
                      </p>
                    </div>
                  </div>
                </AnimatedSection>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Technology Stack ───────────────────────────── */}
        <section id="stack" className="px-6 py-24">
          <div className="mx-auto max-w-6xl">
            <AnimatedSection className="text-center">
              <Badge
                variant="secondary"
                className="mb-4 rounded-full px-3 py-1 text-xs"
              >
                Technology
              </Badge>
              <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
                Powered by{" "}
                <span className="landing-gradient-text italic">
                  modern technology
                </span>
              </h2>
              <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
                Batteries included. No legacy baggage.
              </p>
            </AnimatedSection>

            <AnimatedSection className="mt-16" delay={0.2}>
              <div className="landing-border-glow grid grid-cols-2 gap-px overflow-hidden rounded-2xl sm:grid-cols-4">
                {STACK_ITEMS.map((item) => (
                  <div
                    key={item.label}
                    className="flex flex-col items-center justify-center bg-card/40 p-8 text-center transition-colors hover:bg-card/70"
                  >
                    <span className="text-base font-semibold">{item.label}</span>
                    <span className="mt-1 text-xs text-muted-foreground">
                      {item.desc}
                    </span>
                  </div>
                ))}
              </div>
            </AnimatedSection>
          </div>
        </section>

        {/* ─── Why RL-ERP ─────────────────────────────────── */}
        <section id="why" className="px-6 py-24">
          <div className="mx-auto max-w-6xl">
            <AnimatedSection className="text-center">
              <Badge
                variant="secondary"
                className="mb-4 rounded-full px-3 py-1 text-xs"
              >
                Why RL-ERP
              </Badge>
              <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
                Not another{" "}
                <span className="landing-gradient-text italic">
                  bloated ERP
                </span>
              </h2>
            </AnimatedSection>

            <div className="mt-16 grid gap-6 sm:grid-cols-2">
              {WHY_ITEMS.map((item, i) => (
                <AnimatedSection key={item.title} delay={i * 0.1}>
                  <div className="flex gap-4 rounded-xl border border-border/20 p-6">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-success" />
                    <div>
                      <h3 className="text-sm font-semibold">{item.title}</h3>
                      <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                </AnimatedSection>
              ))}
            </div>
          </div>
        </section>

        {/* ─── CTA ────────────────────────────────────────── */}
        <section className="px-6 py-24">
          <AnimatedSection>
            <div className="mx-auto max-w-3xl text-center">
              <div className="landing-border-glow rounded-3xl p-12">
                <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
                  Ready to{" "}
                  <span className="landing-gradient-text italic">get started</span>?
                </h2>
                <p className="mx-auto mt-4 max-w-md text-muted-foreground">
                  Deploy RL-ERP on your own infrastructure and take control of your business operations.
                </p>
                <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
                  <Link to="/app/dashboard">
                    <Button size="lg" className="gap-2 rounded-xl px-8">
                      Launch Dashboard
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </AnimatedSection>
        </section>

        {/* ─── Footer ─────────────────────────────────────── */}
        <footer className="border-t border-border/30 px-6 py-8">
          <div className="mx-auto flex max-w-6xl items-center justify-between">
            <span className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} RL-ERP
            </span>
            <span className="text-xs text-muted-foreground/60">
              Built with React, FastAPI & PostgreSQL
            </span>
          </div>
        </footer>
      </div>
    </div>
  )
}
