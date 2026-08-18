import { useMemo, useState } from "react"
import { Archive, Eye, Pencil, Plus, Search } from "lucide-react"
import { toast } from "sonner"
import { EmptyState } from "@/components/common/EmptyState"
import { PageHeader } from "@/components/common/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
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
import { useInventoryQuery } from "@/features/inventory/hooks"
import { ProductDetailsDialog } from "@/features/products/components/ProductDetailsDialog"
import { ProductFormDialog } from "@/features/products/components/ProductFormDialog"
import {
  useDeactivateProductMutation,
  useProductsQuery,
} from "@/features/products/hooks"
import {
  PRODUCT_TYPES,
  formatProductType,
  type Product,
  type ProductType,
} from "@/features/products/types"

type ProductTypeFilter = ProductType | "ALL"

function formatMoney(value: Product["standard_cost"]) {
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`
}

export default function ProductsPage() {
  const productsQuery = useProductsQuery()
  const inventoryQuery = useInventoryQuery()
  const deactivateMutation = useDeactivateProductMutation()
  const [search, setSearch] = useState("")
  const [productType, setProductType] = useState<ProductTypeFilter>("ALL")
  const [formOpen, setFormOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [detailProduct, setDetailProduct] = useState<Product | null>(null)
  const [deactivateProduct, setDeactivateProduct] = useState<Product | null>(null)

  const inventoryByProduct = useMemo(
    () => new Map((inventoryQuery.data ?? []).map((item) => [item.product_id, item])),
    [inventoryQuery.data],
  )
  const products = useMemo(() => {
    const term = search.trim().toLowerCase()
    return (productsQuery.data ?? []).filter((product) => {
      const matchesSearch =
        !term ||
        product.name.toLowerCase().includes(term) ||
        product.sku.toLowerCase().includes(term)
      return matchesSearch && (productType === "ALL" || product.product_type === productType)
    })
  }, [productType, productsQuery.data, search])

  const openCreate = () => {
    setEditingProduct(null)
    setFormOpen(true)
  }

  const openEdit = (product: Product) => {
    setEditingProduct(product)
    setFormOpen(true)
  }

  const confirmDeactivate = async () => {
    if (!deactivateProduct) return
    try {
      await deactivateMutation.mutateAsync(deactivateProduct.id)
      toast.success("Product deactivated")
      setDeactivateProduct(null)
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Unable to deactivate product."))
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title="Products"
        description="Manage active product master data and stock settings."
        actions={<Button onClick={openCreate}><Plus className="h-4 w-4" />New Product</Button>}
      />

      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="grid gap-3 border-b border-border-subtle p-4 sm:grid-cols-[minmax(0,1fr)_220px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                className="pl-9"
                placeholder="Search by product or SKU..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
            <Select value={productType} onValueChange={(value) => setProductType(value as ProductTypeFilter)}>
              <SelectTrigger><SelectValue placeholder="All product types" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All product types</SelectItem>
                {PRODUCT_TYPES.map((type) => <SelectItem key={type} value={type}>{formatProductType(type)}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {productsQuery.isLoading ? (
            <div className="space-y-2 p-4">{Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-10 w-full" />)}</div>
          ) : productsQuery.isError ? (
            <EmptyState
              title="Unable to load products."
              description={getApiErrorMessage(productsQuery.error, "Check the API connection and try again.")}
              action={<Button variant="outline" size="sm" onClick={() => void productsQuery.refetch()}>Try again</Button>}
            />
          ) : products.length === 0 ? (
            <EmptyState
              title={productsQuery.data?.length ? "No products match these filters." : "No products yet."}
              description={productsQuery.data?.length ? "Adjust the search or product type filter." : "Create the first product to begin tracking inventory."}
              action={!productsQuery.data?.length ? <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" />New Product</Button> : undefined}
            />
          ) : (
            <>
              <div className="hidden overflow-x-auto md:block">
                <Table>
                  <TableHeader><TableRow>
                    <TableHead>SKU</TableHead><TableHead>Product</TableHead><TableHead>Type</TableHead>
                    <TableHead>Unit</TableHead><TableHead>GST</TableHead><TableHead>Standard cost</TableHead>
                    <TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead>
                  </TableRow></TableHeader>
                  <TableBody>
                    {products.map((product) => (
                      <TableRow key={product.id}>
                        <TableCell className="font-medium">{product.sku}</TableCell>
                        <TableCell>{product.name}</TableCell>
                        <TableCell>{formatProductType(product.product_type)}</TableCell>
                        <TableCell>{product.unit || "—"}</TableCell>
                        <TableCell>{product.gst_rate === null ? "—" : `${product.gst_rate}%`}</TableCell>
                        <TableCell data-numeric>{formatMoney(product.standard_cost)}</TableCell>
                        <TableCell><Badge variant="secondary">Active</Badge></TableCell>
                        <TableCell>
                          <div className="flex justify-end gap-1">
                            <Button variant="ghost" size="icon" onClick={() => setDetailProduct(product)} aria-label={`View ${product.name}`}><Eye className="h-4 w-4" /></Button>
                            <Button variant="ghost" size="icon" onClick={() => openEdit(product)} aria-label={`Edit ${product.name}`}><Pencil className="h-4 w-4" /></Button>
                            <Button variant="ghost" size="icon" onClick={() => setDeactivateProduct(product)} aria-label={`Deactivate ${product.name}`}><Archive className="h-4 w-4" /></Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="divide-y divide-border-subtle md:hidden">
                {products.map((product) => (
                  <div key={product.id} className="space-y-3 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0"><p className="truncate text-sm font-medium">{product.name}</p><p className="mt-0.5 text-xs text-muted-foreground">{product.sku} · {formatProductType(product.product_type)}</p></div>
                      <Badge variant="secondary">Active</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground"><span>Unit: {product.unit || "—"}</span><span>Cost: {formatMoney(product.standard_cost)}</span></div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setDetailProduct(product)}><Eye className="h-4 w-4" />View</Button>
                      <Button variant="outline" size="sm" onClick={() => openEdit(product)}><Pencil className="h-4 w-4" />Edit</Button>
                      <Button variant="ghost" size="sm" onClick={() => setDeactivateProduct(product)}><Archive className="h-4 w-4" />Deactivate</Button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <ProductFormDialog key={`${editingProduct?.id ?? "new"}-${formOpen}`} open={formOpen} onOpenChange={setFormOpen} product={editingProduct} />
      <ProductDetailsDialog
        open={Boolean(detailProduct)}
        onOpenChange={(open) => !open && setDetailProduct(null)}
        product={detailProduct}
        inventory={detailProduct ? inventoryByProduct.get(detailProduct.id) : undefined}
      />

      <Dialog open={Boolean(deactivateProduct)} onOpenChange={(open) => !open && setDeactivateProduct(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Deactivate product?</DialogTitle><DialogDescription>{deactivateProduct?.name} will be removed from active product and inventory views. Existing records remain preserved.</DialogDescription></DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeactivateProduct(null)} disabled={deactivateMutation.isPending}>Cancel</Button>
            <Button variant="destructive" onClick={() => void confirmDeactivate()} disabled={deactivateMutation.isPending}>{deactivateMutation.isPending ? "Deactivating..." : "Deactivate"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
