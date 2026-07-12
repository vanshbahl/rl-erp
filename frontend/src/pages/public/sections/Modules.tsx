import { useRef } from "react"
import { motion, useInView } from "motion/react"
import { Package, Users, Truck, ShoppingCart, FileText, Boxes, Receipt, BarChart3, Settings } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { WorkflowVisualization } from "@/components/simulations/WorkflowVisualization"

const MODULES = [
  { icon: Package, label: "Products", desc: "Catalog & variants" },
  { icon: Users, label: "Customers", desc: "CRM lifecycle" },
  { icon: Truck, label: "Suppliers", desc: "Vendor management" },
  { icon: ShoppingCart, label: "Sales", desc: "Order-to-cash" },
  { icon: FileText, label: "Purchasing", desc: "Procure-to-pay" },
  { icon: Boxes, label: "Inventory", desc: "Warehouse ops" },
  { icon: Receipt, label: "Invoicing", desc: "Billing tracking" },
  { icon: BarChart3, label: "Reports", desc: "Real-time analytics" },
  { icon: Settings, label: "Settings", desc: "Access & config" },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
}

const itemVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.5, ease: "easeOut" } },
}

export function Modules() {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: "100px" })

  return (
    <section id="modules" className="px-6 py-32 bg-card/20 border-y border-border/30">
      <div className="mx-auto max-w-6xl">
        
        {/* Animated Workflow Visualization */}
        <div className="mb-32">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "100px" }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <Badge variant="secondary" className="mb-4 rounded-full px-3 py-1 text-xs">
              Workflow
            </Badge>
            <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
              From raw material to <span className="landing-gradient-text italic">revenue</span>
            </h2>
          </motion.div>
          <WorkflowVisualization />
        </div>

        <div className="grid md:grid-cols-2 gap-16 items-center">
          <motion.div 
            ref={ref}
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <h2 className="font-serif text-3xl tracking-tight sm:text-4xl md:text-5xl">
              Everything your business <span className="landing-gradient-text italic">needs</span>
            </h2>
            <p className="mt-6 text-lg text-muted-foreground">
              Modular by design. Activate what you need, when you need it. As your operations scale, RL-ERP scales with you without expensive enterprise license upgrades.
            </p>
          </motion.div>

          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            className="grid grid-cols-2 sm:grid-cols-3 gap-4"
          >
            {MODULES.map((mod) => (
              <motion.div 
                key={mod.label} 
                variants={itemVariants}
                className="group flex flex-col items-center text-center gap-3 rounded-2xl border border-border/30 bg-background/50 p-6 transition-all duration-300 hover:border-primary/40 hover:bg-card/80 hover:shadow-lg"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 transition-transform duration-300 group-hover:scale-110 group-hover:bg-primary/20">
                  <mod.icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold">{mod.label}</h3>
                  <p className="mt-1 text-[10px] text-muted-foreground opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                    {mod.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
