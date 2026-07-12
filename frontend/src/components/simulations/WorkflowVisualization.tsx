import { useEffect, useRef } from "react"
import { motion, useReducedMotion } from "motion/react"
import { Truck, Package, Settings, ShieldCheck, Warehouse, Users } from "lucide-react"

const NODES = [
  { id: "supplier", icon: Truck, label: "Supplier", x: 10, y: 50 },
  { id: "raw", icon: Package, label: "Raw Materials", x: 30, y: 20 },
  { id: "production", icon: Settings, label: "Production", x: 50, y: 50 },
  { id: "quality", icon: ShieldCheck, label: "Quality Control", x: 70, y: 80 },
  { id: "warehouse", icon: Warehouse, label: "Warehouse", x: 70, y: 20 },
  { id: "customer", icon: Users, label: "Customer", x: 90, y: 50 },
]

const EDGES = [
  { source: "supplier", target: "raw" },
  { source: "raw", target: "production" },
  { source: "production", target: "quality" },
  { source: "quality", target: "warehouse" },
  { source: "warehouse", target: "customer" },
]

export function WorkflowVisualization() {
  const containerRef = useRef<HTMLDivElement>(null)
  const prefersReducedMotion = useReducedMotion()

  // Get coordinates for SVG paths
  const getNodeCoords = (id: string) => {
    const node = NODES.find((n) => n.id === id)
    return node ? { x: `${node.x}%`, y: `${node.y}%` } : { x: "0%", y: "0%" }
  }

  return (
    <div 
      ref={containerRef}
      className="relative h-[400px] w-full max-w-4xl mx-auto rounded-3xl border border-border/20 bg-card/20 p-8 overflow-hidden landing-border-glow"
    >
      <div 
        className="absolute inset-0 w-full h-full"
      >
        {/* Connection Lines (SVG) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ overflow: "visible" }}>
          {EDGES.map((edge, i) => {
            const source = getNodeCoords(edge.source)
            const target = getNodeCoords(edge.target)
            
            return (
              <g key={`${edge.source}-${edge.target}`}>
                {/* Base line */}
                <path
                  d={`M ${source.x} ${source.y} C ${target.x} ${source.y}, ${source.x} ${target.y}, ${target.x} ${target.y}`}
                  fill="none"
                  stroke="var(--color-border)"
                  strokeWidth="2"
                  strokeOpacity="0.4"
                  className="transition-colors"
                />
                
                {/* Animated pulse line */}
                {!prefersReducedMotion && (
                  <motion.path
                    d={`M ${source.x} ${source.y} C ${target.x} ${source.y}, ${source.x} ${target.y}, ${target.x} ${target.y}`}
                    fill="none"
                    stroke="var(--color-primary)"
                    strokeWidth="3"
                    strokeLinecap="round"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ 
                      pathLength: [0, 1, 1],
                      opacity: [0, 1, 0],
                    }}
                    transition={{
                      duration: 8,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: i * 0.8, // Stagger pulses along the network
                    }}
                  />
                )}
              </g>
            )
          })}
        </svg>

        {/* Nodes */}
        {NODES.map((node) => (
          <div
            key={node.id}
            className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center gap-2 group cursor-default"
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
          >
            <div className="relative">
              {/* Outer glow */}
              <div className="absolute inset-0 rounded-full bg-primary/10 blur-xl transition-all duration-500 group-hover:bg-primary/20" />
              
              {/* Core node */}
              <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl border border-border/50 bg-background/80 shadow-sm backdrop-blur-md transition-all duration-300 group-hover:border-primary/40 group-hover:shadow-primary/10">
                <node.icon className="h-6 w-6 text-foreground/70 transition-colors group-hover:text-primary" />
              </div>
            </div>
            <span className="text-xs font-medium text-muted-foreground transition-colors group-hover:text-foreground">
              {node.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
