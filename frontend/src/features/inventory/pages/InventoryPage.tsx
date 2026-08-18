import { useMemo, useState } from "react"
import { SlidersHorizontal } from "lucide-react"
import { EmptyState } from "@/components/common/EmptyState"
import { PageHeader } from "@/components/common/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { getApiErrorMessage } from "@/features/auth/api"
import { InventoryAdjustmentDialog } from "@/features/inventory/components/InventoryAdjustmentDialog"
import { useInventoryQuery, useLowStockQuery } from "@/features/inventory/hooks"
import { getStockStatus, type InventoryItem, type StockStatus } from "@/features/inventory/types"
import { useProductsQuery } from "@/features/products/hooks"
import { PRODUCT_TYPES, formatProductType, type Product, type ProductType } from "@/features/products/types"

type StockFilter = "ALL" | "LOW"
type ProductTypeFilter = "ALL" | ProductType

const statusClassNames: Record<StockStatus, string> = {
  Healthy: "border-success/15 bg-success/10 text-success",
  "Low Stock": "border-warning/15 bg-warning/10 text-warning",
  "Out of Stock": "border-destructive/15 bg-destructive/10 text-destructive",
}

export default function InventoryPage() {
  const [stockFilter, setStockFilter] = useState<StockFilter>("ALL")
  const [productType, setProductType] = useState<ProductTypeFilter>("ALL")
  const inventoryQuery = useInventoryQuery()
  const lowStockQuery = useLowStockQuery(productType === "ALL" ? {} : { productType })
  const productsQuery = useProductsQuery()
  const [adjustmentItem, setAdjustmentItem] = useState<InventoryItem | null>(null)

  const productsById = useMemo(
    () => new Map((productsQuery.data ?? []).map((product) => [product.id, product])),
    [productsQuery.data],
  )
  const items = useMemo(() => {
    const source = stockFilter === "LOW" ? (lowStockQuery.data ?? []) : (inventoryQuery.data ?? [])
    return source.filter((item) => {
      const product = productsById.get(item.product_id)
      return product && (productType === "ALL" || product.product_type === productType)
    })
  }, [inventoryQuery.data, lowStockQuery.data, productType, productsById, stockFilter])
  const activeQuery = stockFilter === "LOW" ? lowStockQuery : inventoryQuery
  const adjustmentProduct = adjustmentItem ? productsById.get(adjustmentItem.product_id) ?? null : null

  const statusBadge = (item: InventoryItem) => {
    const status = getStockStatus(item)
    return <Badge variant="outline" className={statusClassNames[status]}>{status}</Badge>
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Inventory" description="Monitor available quantities and maintain verified stock levels." />
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="grid gap-3 border-b border-border-subtle p-4 sm:grid-cols-2">
            <Select value={stockFilter} onValueChange={(value) => setStockFilter(value as StockFilter)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent><SelectItem value="ALL">All stock</SelectItem><SelectItem value="LOW">Low stock only</SelectItem></SelectContent>
            </Select>
            <Select value={productType} onValueChange={(value) => setProductType(value as ProductTypeFilter)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All product types</SelectItem>
                {PRODUCT_TYPES.map((type) => <SelectItem key={type} value={type}>{formatProductType(type)}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {activeQuery.isLoading || productsQuery.isLoading ? (
            <div className="space-y-2 p-4">{Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-10 w-full" />)}</div>
          ) : activeQuery.isError || productsQuery.isError ? (
            <EmptyState
              title="Unable to load inventory."
              description={getApiErrorMessage(activeQuery.error ?? productsQuery.error, "Check the API connection and try again.")}
              action={<Button variant="outline" size="sm" onClick={() => { void activeQuery.refetch(); void productsQuery.refetch() }}>Try again</Button>}
            />
          ) : items.length === 0 ? (
            <EmptyState title={stockFilter === "LOW" ? "No low stock items." : "No inventory records found."} description={stockFilter === "LOW" ? "Current stock levels are above their configured minimums." : "Inventory records appear automatically when products are created."} />
          ) : (
            <>
              <div className="hidden overflow-x-auto md:block">
                <Table>
                  <TableHeader><TableRow><TableHead>Product</TableHead><TableHead>Type</TableHead><TableHead>Available</TableHead><TableHead>Minimum</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Action</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {items.map((item) => {
                      const product = productsById.get(item.product_id) as Product
                      return <TableRow key={item.id}>
                        <TableCell><p className="font-medium">{product.name}</p><p className="text-[11px] text-muted-foreground">{product.sku}</p></TableCell>
                        <TableCell>{formatProductType(product.product_type)}</TableCell>
                        <TableCell data-numeric>{item.quantity} {product.unit || "units"}</TableCell>
                        <TableCell data-numeric>{item.minimum_stock} {product.unit || "units"}</TableCell>
                        <TableCell>{statusBadge(item)}</TableCell>
                        <TableCell className="text-right"><Button variant="outline" size="sm" onClick={() => setAdjustmentItem(item)}><SlidersHorizontal className="h-4 w-4" />Adjust</Button></TableCell>
                      </TableRow>
                    })}
                  </TableBody>
                </Table>
              </div>
              <div className="divide-y divide-border-subtle md:hidden">
                {items.map((item) => {
                  const product = productsById.get(item.product_id) as Product
                  return <div key={item.id} className="space-y-3 p-4">
                    <div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="truncate text-sm font-medium">{product.name}</p><p className="text-xs text-muted-foreground">{product.sku} · {formatProductType(product.product_type)}</p></div>{statusBadge(item)}</div>
                    <div className="grid grid-cols-2 gap-2 rounded-md bg-secondary/65 p-3 text-xs"><div><p className="text-muted-foreground">Available</p><p className="mt-1 font-medium">{item.quantity} {product.unit || "units"}</p></div><div><p className="text-muted-foreground">Minimum</p><p className="mt-1 font-medium">{item.minimum_stock} {product.unit || "units"}</p></div></div>
                    <Button variant="outline" size="sm" onClick={() => setAdjustmentItem(item)}><SlidersHorizontal className="h-4 w-4" />Adjust inventory</Button>
                  </div>
                })}
              </div>
            </>
          )}
        </CardContent>
      </Card>
      <InventoryAdjustmentDialog key={`${adjustmentItem?.id ?? "none"}-${Boolean(adjustmentItem)}`} open={Boolean(adjustmentItem)} onOpenChange={(open) => !open && setAdjustmentItem(null)} item={adjustmentItem} product={adjustmentProduct} />
    </div>
  )
}
