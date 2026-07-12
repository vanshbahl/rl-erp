import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Package,
  ShoppingCart,
  Users,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

type Stat = {
  title: string
  value: string
  change: string
  trend: "up" | "down" | "neutral"
  icon: LucideIcon
}

const STATS: Stat[] = [
  {
    title: "Total Revenue",
    value: "$0",
    change: "+0%",
    trend: "up" as const,
    icon: TrendingUp,
  },
  {
    title: "Products",
    value: "0",
    change: "0 active",
    trend: "neutral" as const,
    icon: Package,
  },
  {
    title: "Orders",
    value: "0",
    change: "0 pending",
    trend: "neutral" as const,
    icon: ShoppingCart,
  },
  {
    title: "Customers",
    value: "0",
    change: "0 new",
    trend: "neutral" as const,
    icon: Users,
  },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Welcome to RL-ERP. Connect your backend to see live data.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map((stat) => (
          <Card key={stat.title} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                {stat.trend === "up" && (
                  <ArrowUpRight className="h-3 w-3 text-success" />
                )}
                {stat.trend === "down" && (
                  <ArrowDownRight className="h-3 w-3 text-destructive" />
                )}
                <span>{stat.change}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-base">Recent Orders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
              <div className="text-center">
                <ShoppingCart className="mx-auto mb-2 h-8 w-8 opacity-30" />
                <p>No orders yet</p>
                <Badge variant="secondary" className="mt-2 text-xs">
                  Connect API
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-base">Low Stock Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
              <div className="text-center">
                <Package className="mx-auto mb-2 h-8 w-8 opacity-30" />
                <p>No alerts</p>
                <Badge variant="secondary" className="mt-2 text-xs">
                  Connect API
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
