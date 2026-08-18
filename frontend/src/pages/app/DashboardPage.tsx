import { EmptyState } from "@/components/common/EmptyState"
import { PageHeader } from "@/components/common/PageHeader"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Boxes,
  CreditCard,
  IndianRupee,
  PackagePlus,
  ShoppingCart,
  UserPlus,
  Users,
} from "lucide-react"

interface DashboardPanelProps {
  title: string
  columns: string[]
  emptyTitle: string
  className?: string
}

function DashboardPanel({
  title,
  columns,
  emptyTitle,
  className,
}: DashboardPanelProps) {
  return (
    <Card className={`min-w-0 overflow-hidden ${className ?? ""}`}>
      <CardHeader className="border-b border-border-subtle px-4 py-3.5">
        <CardTitle className="text-[14px]">{title}</CardTitle>
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
        <EmptyState title={emptyTitle} className="min-h-32" />
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        title="Dashboard"
        description="A concise view of sales, receivables, and inventory attention items."
        className="border-0 pb-0"
      />

      <section aria-label="Key business indicators" className="grid gap-4 lg:grid-cols-12">
        <Card className="overflow-hidden lg:col-span-5">
          <CardContent className="flex min-h-40 flex-col justify-between p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium">Outstanding receivables</p>
                <p className="mt-1 text-xs text-muted-foreground">Current unpaid invoice balance</p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-md bg-accent text-primary">
                <IndianRupee className="h-[18px] w-[18px]" />
              </div>
            </div>
            <div>
              <p className="text-[30px] font-semibold leading-none tracking-tight" data-numeric>₹0</p>
              <p className="mt-2 text-xs text-muted-foreground">0 open invoices</p>
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden p-2 lg:col-span-3">
          <div className="grid h-full gap-2 min-[390px]:grid-cols-2 lg:grid-cols-1">
            <div className="flex min-h-18 items-center justify-between rounded-md bg-secondary/75 p-3.5">
              <div>
                <p className="text-xs text-muted-foreground">Sales orders</p>
                <p className="mt-1 text-2xl font-semibold leading-none" data-numeric>0</p>
                <p className="mt-1.5 text-[11px] text-muted-foreground">0 pending</p>
              </div>
              <ShoppingCart className="h-[18px] w-[18px] text-muted-foreground" />
            </div>
            <div className="flex min-h-18 items-center justify-between rounded-md bg-secondary/75 p-3.5">
              <div>
                <p className="text-xs text-muted-foreground">Active customers</p>
                <p className="mt-1 text-2xl font-semibold leading-none" data-numeric>0</p>
                <p className="mt-1.5 text-[11px] text-muted-foreground">Customer records</p>
              </div>
              <Users className="h-[18px] w-[18px] text-muted-foreground" />
            </div>
          </div>
        </Card>

        <Card className="overflow-hidden lg:col-span-4">
          <CardContent className="flex min-h-40 flex-col justify-between p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium">Low stock</p>
                <p className="mt-1 text-xs text-muted-foreground">Items below minimum quantity</p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-md bg-warning/10 text-warning">
                <Boxes className="h-[18px] w-[18px]" />
              </div>
            </div>
            <div>
              <p className="text-[30px] font-semibold leading-none tracking-tight" data-numeric>0</p>
              <p className="mt-2 text-xs text-muted-foreground">No items require attention</p>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid min-w-0 gap-4 lg:grid-cols-12">
        <DashboardPanel
          title="Recent Sales Orders"
          columns={["Order", "Customer", "Status", "Amount"]}
          emptyTitle="No sales orders yet."
          className="lg:col-span-8"
        />
        <DashboardPanel
          title="Low Stock"
          columns={["Product", "Available", "Minimum"]}
          emptyTitle="No low stock items."
          className="lg:col-span-4"
        />

        <DashboardPanel
          title="Outstanding Invoices"
          columns={["Invoice", "Customer", "Outstanding"]}
          emptyTitle="No outstanding invoices."
          className="lg:col-span-8"
        />

        <Card className="overflow-hidden lg:col-span-4">
          <CardHeader className="border-b border-border-subtle px-4 py-3.5">
            <CardTitle className="text-[14px]">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2 p-4 lg:grid-cols-1">
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs text-muted-foreground disabled:opacity-75" disabled>
              <PackagePlus className="h-4 w-4" />
              New Product
            </Button>
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs text-muted-foreground disabled:opacity-75" disabled>
              <UserPlus className="h-4 w-4" />
              New Customer
            </Button>
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs text-muted-foreground disabled:opacity-75" disabled>
              <ShoppingCart className="h-4 w-4" />
              Sales Order
            </Button>
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs text-muted-foreground disabled:opacity-75" disabled>
              <CreditCard className="h-4 w-4" />
              Record Payment
            </Button>
            <p className="col-span-2 mt-1 text-[11px] leading-4 text-muted-foreground lg:col-span-1">
              Actions become available as Phase 1 modules are connected.
            </p>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
