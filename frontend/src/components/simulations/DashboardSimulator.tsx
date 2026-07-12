import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { Package, Truck, Settings, Receipt, CircleDollarSign, CheckCircle2, TrendingUp, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

type Phase = 
  | "IDLE"
  | "SUPPLIER_SHIPS" 
  | "INVENTORY_UP" 
  | "PRODUCTION_STARTS" 
  | "FINISHED_GOODS" 
  | "SALES_ORDER" 
  | "INVOICE" 
  | "REVENUE_UP"

interface EventLog {
  id: string
  time: string
  message: string
  icon: React.ElementType
  color: string
}

export function DashboardSimulator() {
  const [phase, setPhase] = useState<Phase>("IDLE")
  const [revenue, setRevenue] = useState(284500)
  const [rawMaterials, setRawMaterials] = useState(140)
  const [finishedGoods, setFinishedGoods] = useState(85)
  const [machineStatus, setMachineStatus] = useState<"IDLE" | "RUNNING">("IDLE")
  const [events, setEvents] = useState<EventLog[]>([
    { id: "e1", time: "10:42 AM", message: "System online.", icon: CheckCircle2, color: "text-success" }
  ])
  const [chartData, setChartData] = useState([40, 55, 45, 60, 75, 65, 80, 70, 85, 90, 78, 95])

  const addEvent = (message: string, icon: React.ElementType, color: string) => {
    setEvents(prev => {
      const now = new Date()
      const time = `${now.getHours() % 12 || 12}:${now.getMinutes().toString().padStart(2, "0")} ${now.getHours() >= 12 ? 'PM' : 'AM'}`
      return [{ id: Math.random().toString(), time, message, icon, color }, ...prev].slice(0, 4)
    })
  }

  // Master timeline loop
  useEffect(() => {
    let timeoutId: number
    
    const runSequence = async () => {
      // 1. Supplier Ships
      setPhase("SUPPLIER_SHIPS")
      addEvent("Supplier PO-442 in transit", Truck, "text-blue-500")
      await new Promise(r => setTimeout(r, 2000))

      // 2. Inventory Increases
      setPhase("INVENTORY_UP")
      setRawMaterials(prev => prev + 500)
      addEvent("Raw materials received (+500)", Package, "text-success")
      await new Promise(r => setTimeout(r, 1500))

      // 3. Production Starts
      setPhase("PRODUCTION_STARTS")
      setMachineStatus("RUNNING")
      setRawMaterials(prev => prev - 200)
      addEvent("Production run PR-091 started", Settings, "text-warning")
      await new Promise(r => setTimeout(r, 2500))

      // 4. Finished Goods
      setPhase("FINISHED_GOODS")
      setMachineStatus("IDLE")
      setFinishedGoods(prev => prev + 50)
      addEvent("PR-091 complete (+50 units)", CheckCircle2, "text-success")
      await new Promise(r => setTimeout(r, 1500))

      // 5. Sales Order
      setPhase("SALES_ORDER")
      setFinishedGoods(prev => prev - 12)
      addEvent("New sales order SO-992", Package, "text-purple-500")
      await new Promise(r => setTimeout(r, 1500))

      // 6. Invoice
      setPhase("INVOICE")
      addEvent("Invoice INV-992 generated", Receipt, "text-blue-500")
      await new Promise(r => setTimeout(r, 1500))

      // 7. Revenue Updates
      setPhase("REVENUE_UP")
      setRevenue(prev => prev + 4250)
      setChartData(prev => [...prev.slice(1), prev[prev.length - 1] + (Math.random() * 10)])
      addEvent("Payment received ($4,250)", CircleDollarSign, "text-success")
      await new Promise(r => setTimeout(r, 2000))

      // Loop back
      setPhase("IDLE")
      timeoutId = window.setTimeout(runSequence, 3000)
    }

    // Start slightly delayed
    timeoutId = window.setTimeout(runSequence, 1000)

    return () => clearTimeout(timeoutId)
  }, [])

  return (
    <div className="landing-border-glow overflow-hidden rounded-2xl p-1 shadow-2xl">
      <div className="rounded-xl bg-card">
        {/* Browser Mock */}
        <div className="flex items-center gap-2 border-b border-border/50 bg-muted/20 px-4 py-3 backdrop-blur-sm">
          <div className="flex gap-1.5">
            <div className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
            <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
            <div className="h-2.5 w-2.5 rounded-full bg-green-500/80" />
          </div>
          <div className="ml-4 flex-1 rounded-md bg-background/50 px-3 py-1.5 text-xs text-muted-foreground shadow-sm">
            <span className="opacity-50">https://</span>app.rl-erp.com<span className="opacity-50">/dashboard</span>
          </div>
        </div>
        
        {/* Dashboard Content */}
        <div className="p-6">
          <div className="grid gap-4 sm:grid-cols-4">
            {/* Revenue Metric */}
            <motion.div 
              animate={phase === "REVENUE_UP" ? { borderColor: ["var(--color-border)", "var(--color-success)", "var(--color-border)"] } : {}}
              transition={{ duration: 0.5 }}
              className="rounded-lg border border-border/50 bg-background/40 p-4"
            >
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <CircleDollarSign className="h-3.5 w-3.5" />
                Revenue
              </div>
              <p className="mt-1.5 text-2xl font-semibold tabular-nums">
                ${revenue.toLocaleString()}
              </p>
              <p className="mt-1 flex items-center gap-1 text-xs text-success">
                <TrendingUp className="h-3 w-3" />
                +12.5%
              </p>
            </motion.div>

            {/* Raw Materials Metric */}
            <motion.div 
              animate={phase === "INVENTORY_UP" ? { borderColor: ["var(--color-border)", "var(--color-primary)", "var(--color-border)"] } : phase === "PRODUCTION_STARTS" ? { borderColor: ["var(--color-border)", "var(--color-warning)", "var(--color-border)"] } : {}}
              className="rounded-lg border border-border/50 bg-background/40 p-4"
            >
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Package className="h-3.5 w-3.5" />
                Raw Materials
              </div>
              <p className="mt-1.5 text-2xl font-semibold tabular-nums">
                {rawMaterials} kg
              </p>
              <p className={cn("mt-1 flex items-center gap-1 text-xs", rawMaterials < 200 ? "text-destructive" : "text-muted-foreground")}>
                {rawMaterials < 200 ? <><AlertCircle className="h-3 w-3"/> Low stock</> : "Healthy"}
              </p>
            </motion.div>

            {/* Finished Goods Metric */}
            <motion.div 
              animate={phase === "SALES_ORDER" ? { opacity: [1, 0.8, 1] } : {}}
              className="rounded-lg border border-border/50 bg-background/40 p-4"
            >
               <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Package className="h-3.5 w-3.5" />
                Finished Goods
              </div>
              <p className="mt-1.5 text-2xl font-semibold tabular-nums">
                {finishedGoods} units
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Ready to ship
              </p>
            </motion.div>

            {/* Machine Status Metric */}
            <motion.div 
              animate={machineStatus === "RUNNING" ? { borderColor: "var(--color-warning)" } : {}}
              className="relative overflow-hidden rounded-lg border border-border/50 bg-background/40 p-4"
            >
              {machineStatus === "RUNNING" && (
                 <motion.div 
                   className="absolute inset-0 bg-warning/5"
                   animate={{ opacity: [0.5, 1, 0.5] }}
                   transition={{ repeat: Infinity, duration: 1.5 }}
                 />
              )}
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Settings className={cn("h-3.5 w-3.5", machineStatus === "RUNNING" && "animate-spin")} />
                CNC Line 1
              </div>
              <p className="mt-1.5 text-xl font-semibold">
                {machineStatus === "RUNNING" ? "Running" : "Idle"}
              </p>
              <p className={cn("mt-1 text-xs", machineStatus === "RUNNING" ? "text-warning" : "text-muted-foreground")}>
                {machineStatus === "RUNNING" ? "Job PR-091" : "Awaiting job"}
              </p>
            </motion.div>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {/* Chart Area */}
            <div className="col-span-2 rounded-lg border border-border/50 bg-background/40 p-4">
              <p className="mb-4 text-xs font-medium text-muted-foreground">
                Revenue Trend (Live)
              </p>
              <div className="flex h-32 items-end gap-1.5">
                <AnimatePresence initial={false}>
                  {chartData.map((h, i) => (
                    <motion.div
                      key={i}
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: `${h}%`, opacity: 1 }}
                      transition={{ type: "spring", stiffness: 100, damping: 20 }}
                      className="flex-1 rounded-sm bg-primary/40 dark:bg-primary/60"
                      style={{
                        borderTop: i === chartData.length - 1 ? "2px solid var(--color-primary)" : "none",
                        opacity: i === chartData.length - 1 && phase === "REVENUE_UP" ? 1 : 0.8
                      }}
                    />
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Live Event Stream */}
            <div className="rounded-lg border border-border/50 bg-background/40 p-4">
              <p className="mb-4 text-xs font-medium text-muted-foreground flex items-center justify-between">
                Live Activity
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
                </span>
              </p>
              <div className="space-y-3 overflow-hidden">
                <AnimatePresence initial={false}>
                  {events.map((evt) => (
                    <motion.div
                      key={evt.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex items-start gap-3 text-xs"
                    >
                      <div className={cn("mt-0.5 rounded-full bg-background p-1 border border-border/50", evt.color)}>
                        <evt.icon className="h-3 w-3" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-foreground">{evt.message}</p>
                        <p className="mt-0.5 text-muted-foreground/60">{evt.time}</p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
