import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import type { InventoryItem } from "@/features/inventory/types"
import { formatProductType, type Product } from "@/features/products/types"

interface ProductDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  product: Product | null
  inventory?: InventoryItem
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-secondary/65 p-3">
      <p className="text-[11px] text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm text-foreground">{value}</p>
    </div>
  )
}

export function ProductDetailsDialog({
  open,
  onOpenChange,
  product,
  inventory,
}: ProductDetailsDialogProps) {
  if (!product) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <div className="flex items-center gap-2 pr-8">
            <DialogTitle>{product.name}</DialogTitle>
            <Badge variant={product.is_active ? "secondary" : "outline"}>{product.is_active ? "Active" : "Inactive"}</Badge>
          </div>
          <DialogDescription>{product.sku} · {formatProductType(product.product_type)}</DialogDescription>
        </DialogHeader>

        <div className="grid gap-2 sm:grid-cols-2">
          <Detail label="Unit" value={product.unit || "Not set"} />
          <Detail label="HSN code" value={product.hsn_code || "Not set"} />
          <Detail label="GST rate" value={product.gst_rate === null ? "Not set" : `${product.gst_rate}%`} />
          <Detail label="Base price" value={product.base_price === null ? "Not set" : `₹${Number(product.base_price).toLocaleString("en-IN")}`} />
          <Detail label="Standard cost" value={`₹${Number(product.standard_cost).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`} />
          <Detail label="Color" value={product.color || "Not set"} />
          <Detail label="Available quantity" value={inventory ? `${inventory.quantity} ${product.unit || "units"}` : "Inventory unavailable"} />
          <Detail label="Minimum stock" value={inventory ? `${inventory.minimum_stock} ${product.unit || "units"}` : "Inventory unavailable"} />
        </div>

        {product.description && (
          <div className="rounded-md border border-border-subtle p-3">
            <p className="text-[11px] text-muted-foreground">Description</p>
            <p className="mt-1 text-sm leading-5">{product.description}</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
