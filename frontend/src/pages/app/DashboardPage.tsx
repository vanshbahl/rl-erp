import { EmptyState } from "@/components/common/EmptyState"
import { PageHeader } from "@/components/common/PageHeader"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useLowStockQuery } from "@/features/inventory/hooks"
import { useCustomersQuery } from "@/features/customers/hooks"
import { useOrdersQuery } from "@/features/orders/hooks"
import { formatOrderStatus } from "@/features/orders/types"
import { useOutstandingQuery } from "@/features/payments/hooks"
import { useProductsQuery } from "@/features/products/hooks"
import { useMemo } from "react"
import { useNavigate } from "react-router-dom"
import {
  Boxes,
  CreditCard,
  IndianRupee,
  PackagePlus,
  ShoppingCart,
  UserPlus,
} from "lucide-react"

export default function DashboardPage() {
  const navigate = useNavigate()
  const productsQuery = useProductsQuery()
  const lowStockQuery = useLowStockQuery()
  const customersQuery = useCustomersQuery()
  const ordersQuery = useOrdersQuery()
  const outstandingQuery = useOutstandingQuery()
  const productsById = useMemo(
    () => new Map((productsQuery.data ?? []).map((product) => [product.id, product])),
    [productsQuery.data],
  )
  const lowStockItems = useMemo(
    () => (lowStockQuery.data ?? []).filter((item) => productsById.has(item.product_id)),
    [lowStockQuery.data, productsById],
  )
  const productsValue = productsQuery.isLoading ? "…" : productsQuery.isError ? "—" : String(productsQuery.data?.length ?? 0)
  const lowStockValue = lowStockQuery.isLoading || productsQuery.isLoading ? "…" : lowStockQuery.isError || productsQuery.isError ? "—" : String(lowStockItems.length)
  const orderCount = ordersQuery.isLoading ? "…" : ordersQuery.isError ? "—" : String(ordersQuery.data?.length ?? 0)
  const pendingOrders = (ordersQuery.data ?? []).filter((order) => order.status === "PENDING").length
  const activeCustomers = customersQuery.isLoading ? "…" : customersQuery.isError ? "—" : String(customersQuery.data?.length ?? 0)
  const receivables = (outstandingQuery.data ?? []).reduce((sum, item) => sum + item.outstanding_amount, 0)
  const receivablesValue = outstandingQuery.isLoading ? "…" : outstandingQuery.isError ? "—" : `₹${receivables.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`
  const recentOrders = useMemo(() => [...(ordersQuery.data ?? [])].sort((a, b) => b.id - a.id).slice(0, 5), [ordersQuery.data])

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
              <p className="text-[30px] font-semibold leading-none tracking-tight" data-numeric>{receivablesValue}</p>
              <p className="mt-2 text-xs text-muted-foreground">{outstandingQuery.isLoading ? "Loading invoices..." : `${outstandingQuery.data?.length ?? 0} open invoice${(outstandingQuery.data?.length ?? 0) === 1 ? "" : "s"}`}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden p-2 lg:col-span-3">
          <div className="grid h-full gap-2 min-[390px]:grid-cols-2 lg:grid-cols-1">
            <div className="flex min-h-18 items-center justify-between rounded-md bg-secondary/75 p-3.5">
              <div>
                <p className="text-xs text-muted-foreground">Sales orders</p>
                <p className="mt-1 text-2xl font-semibold leading-none" data-numeric>{orderCount}</p>
                <p className="mt-1.5 text-[11px] text-muted-foreground">{pendingOrders} pending</p>
              </div>
              <ShoppingCart className="h-[18px] w-[18px] text-muted-foreground" />
            </div>
            <div className="flex min-h-18 items-center justify-between rounded-md bg-secondary/75 p-3.5">
              <div>
                <p className="text-xs text-muted-foreground">Active customers</p>
                <p className="mt-1 text-2xl font-semibold leading-none" data-numeric>{activeCustomers}</p>
                <p className="mt-1.5 text-[11px] text-muted-foreground">Customer records</p>
              </div>
              <PackagePlus className="h-[18px] w-[18px] text-muted-foreground" />
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
              <p className="text-[30px] font-semibold leading-none tracking-tight" data-numeric>{lowStockValue}</p>
              <p className="mt-2 text-xs text-muted-foreground">{lowStockItems.length ? `${lowStockItems.length} item${lowStockItems.length === 1 ? " requires" : "s require"} attention` : "No items require attention"} · {productsValue} active products</p>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid min-w-0 gap-4 lg:grid-cols-12">
        <Card className="min-w-0 overflow-hidden lg:col-span-8">
          <CardHeader className="border-b border-border-subtle px-4 py-3.5"><CardTitle className="text-[14px]">Recent Sales Orders</CardTitle></CardHeader>
          <CardContent className="p-0"><Table><TableHeader><TableRow className="hover:bg-transparent"><TableHead>Order</TableHead><TableHead>Customer</TableHead><TableHead>Status</TableHead><TableHead>Amount</TableHead></TableRow></TableHeader><TableBody>{recentOrders.map((order) => <TableRow key={order.id} className="cursor-pointer" onClick={() => navigate("/app/sales")}><TableCell className="font-medium">SO-{String(order.id).padStart(5, "0")}</TableCell><TableCell>{customersQuery.data?.find((customer) => customer.id === order.customer_id)?.company_name ?? `Customer #${order.customer_id}`}</TableCell><TableCell>{formatOrderStatus(order.status)}</TableCell><TableCell data-numeric>₹{Number(order.total_amount).toLocaleString("en-IN", { maximumFractionDigits: 2 })}</TableCell></TableRow>)}</TableBody></Table>{!ordersQuery.isLoading && recentOrders.length === 0 && <EmptyState title={ordersQuery.isError ? "Unable to load sales orders." : "No sales orders yet."} className="min-h-32" />}</CardContent>
        </Card>
        <Card className="min-w-0 overflow-hidden lg:col-span-4">
          <CardHeader className="flex-row items-center justify-between border-b border-border-subtle px-4 py-3.5">
            <CardTitle className="text-[14px]">Low Stock</CardTitle>
            <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => navigate("/app/inventory")}>View inventory</Button>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader><TableRow className="hover:bg-transparent"><TableHead>Product</TableHead><TableHead>Available</TableHead><TableHead>Minimum</TableHead></TableRow></TableHeader>
              <TableBody>
                {lowStockItems.slice(0, 5).map((item) => {
                  const product = productsById.get(item.product_id)
                  if (!product) return null
                  return <TableRow key={item.id} className="cursor-pointer" onClick={() => navigate("/app/inventory")}>
                    <TableCell className="max-w-36 truncate font-medium">{product.name}</TableCell>
                    <TableCell data-numeric>{item.quantity} {product.unit || ""}</TableCell>
                    <TableCell data-numeric>{item.minimum_stock} {product.unit || ""}</TableCell>
                  </TableRow>
                })}
              </TableBody>
            </Table>
            {!lowStockQuery.isLoading && !productsQuery.isLoading && lowStockItems.length === 0 && <EmptyState title={lowStockQuery.isError || productsQuery.isError ? "Unable to load low stock." : "No low stock items."} className="min-h-32" />}
          </CardContent>
        </Card>

        <Card className="min-w-0 overflow-hidden lg:col-span-8"><CardHeader className="border-b border-border-subtle px-4 py-3.5"><CardTitle className="text-[14px]">Outstanding Invoices</CardTitle></CardHeader><CardContent className="p-0"><Table><TableHeader><TableRow className="hover:bg-transparent"><TableHead>Invoice</TableHead><TableHead>Customer</TableHead><TableHead>Outstanding</TableHead></TableRow></TableHeader><TableBody>{(outstandingQuery.data ?? []).slice(0, 5).map((invoice) => <TableRow key={invoice.invoice_id} className="cursor-pointer" onClick={() => navigate("/app/invoices")}><TableCell className="font-medium">{invoice.invoice_number}</TableCell><TableCell>{invoice.company_name}</TableCell><TableCell data-numeric>₹{invoice.outstanding_amount.toLocaleString("en-IN", { maximumFractionDigits: 2 })}</TableCell></TableRow>)}</TableBody></Table>{!outstandingQuery.isLoading && !(outstandingQuery.data ?? []).length && <EmptyState title={outstandingQuery.isError ? "Unable to load outstanding invoices." : "No outstanding invoices."} className="min-h-32" />}</CardContent></Card>

        <Card className="overflow-hidden lg:col-span-4">
          <CardHeader className="border-b border-border-subtle px-4 py-3.5">
            <CardTitle className="text-[14px]">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2 p-4 lg:grid-cols-1">
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs" onClick={() => navigate("/app/products") }>
              <PackagePlus className="h-4 w-4" />
              New Product
            </Button>
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs" onClick={() => navigate("/app/customers") }>
              <UserPlus className="h-4 w-4" />
              New Customer
            </Button>
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs" onClick={() => navigate("/app/sales") }>
              <ShoppingCart className="h-4 w-4" />
              Sales Order
            </Button>
            <Button variant="outline" className="h-9 justify-start border-border-subtle bg-secondary/65 text-xs" onClick={() => navigate("/app/invoices") }>
              <CreditCard className="h-4 w-4" />
              Record Payment
            </Button>
            <p className="col-span-2 mt-1 text-[11px] leading-4 text-muted-foreground lg:col-span-1">
              Create records and record payments from the related invoice detail.
            </p>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
