import { EmptyState } from "@/components/common/EmptyState"
import { PageHeader } from "@/components/common/PageHeader"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const METRICS = [
  { label: "Products", value: "0", detail: "Active products" },
  { label: "Pending Orders", value: "0", detail: "Awaiting action" },
  { label: "Low Stock", value: "0", detail: "Items below minimum" },
  { label: "Outstanding Receivables", value: "₹0", detail: "Pending collection" },
]

interface DashboardPanelProps {
  title: string
  columns: string[]
  emptyTitle: string
  emptyDescription: string
}

function DashboardPanel({
  title,
  columns,
  emptyTitle,
  emptyDescription,
}: DashboardPanelProps) {
  return (
    <Card className="min-w-0">
      <CardHeader className="border-b border-border py-3">
        <CardTitle className="text-[15px]">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {columns.map((column) => (
                <TableHead key={column}>{column}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody />
        </Table>
        <EmptyState title={emptyTitle} description={emptyDescription} />
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  return (
    <div className="space-y-5">
      <PageHeader title="Dashboard" description="Operational overview" />

      <section aria-label="Key performance indicators" className="grid grid-cols-1 border-l border-t border-border min-[390px]:grid-cols-2 lg:grid-cols-4">
        {METRICS.map((metric) => (
          <div key={metric.label} className="min-w-0 border-b border-r border-border bg-card p-4">
            <p className="truncate text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">
              {metric.label}
            </p>
            <p className="mt-2 text-2xl font-semibold leading-none tracking-tight" data-numeric>
              {metric.value}
            </p>
            <p className="mt-2 truncate text-xs text-muted-foreground">{metric.detail}</p>
          </div>
        ))}
      </section>

      <section className="grid min-w-0 gap-4 lg:grid-cols-2">
        <DashboardPanel
          title="Recent Sales Orders"
          columns={["Order", "Customer", "Status", "Amount"]}
          emptyTitle="No sales orders found."
          emptyDescription="Recent sales orders will appear here once they are available."
        />
        <DashboardPanel
          title="Low Stock Alerts"
          columns={["Product", "Available", "Minimum"]}
          emptyTitle="No low stock alerts."
          emptyDescription="Products below their minimum stock level will appear here."
        />
        <DashboardPanel
          title="Outstanding Invoices"
          columns={["Invoice", "Customer", "Outstanding"]}
          emptyTitle="No outstanding invoices."
          emptyDescription="Unpaid and partially paid invoices will appear here."
        />
        <DashboardPanel
          title="Recent Activity"
          columns={["Activity", "Reference", "Time"]}
          emptyTitle="No recent activity."
          emptyDescription="Operational updates will appear here when dashboard data is connected."
        />
      </section>
    </div>
  )
}
