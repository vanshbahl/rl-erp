import { useState, type FormEvent } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { getApiErrorMessage } from "@/features/auth/api"
import { useUpdateInventoryMutation } from "@/features/inventory/hooks"
import type { InventoryItem } from "@/features/inventory/types"
import type { Product } from "@/features/products/types"

interface InventoryAdjustmentDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  item: InventoryItem | null
  product: Product | null
}

export function InventoryAdjustmentDialog({
  open,
  onOpenChange,
  item,
  product,
}: InventoryAdjustmentDialogProps) {
  const updateMutation = useUpdateInventoryMutation()
  const [quantity, setQuantity] = useState(() => item ? String(item.quantity) : "")
  const [minimumStock, setMinimumStock] = useState(() => item ? String(item.minimum_stock) : "")
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!item) return

    const newQuantity = Number(quantity)
    const newMinimumStock = Number(minimumStock)
    if (![newQuantity, newMinimumStock].every(Number.isFinite) || newQuantity < 0 || newMinimumStock < 0) {
      setError("Quantity and minimum stock must be valid non-negative numbers.")
      return
    }

    try {
      await updateMutation.mutateAsync({
        productId: item.product_id,
        payload: { quantity: newQuantity, minimum_stock: newMinimumStock },
      })
      toast.success("Inventory adjusted")
      onOpenChange(false)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to adjust inventory."))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Adjust Inventory</DialogTitle>
          <DialogDescription>
            Set the verified quantity for {product?.name ?? "this product"}. Quantity changes are recorded in the inventory ledger.
          </DialogDescription>
        </DialogHeader>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="rounded-md bg-secondary/65 p-3 text-sm">
            <p className="font-medium">{product?.name ?? "Product"}</p>
            <p className="mt-1 text-xs text-muted-foreground">Current quantity: {item?.quantity ?? 0} {product?.unit || "units"}</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="inventory-quantity">New quantity</Label>
              <Input id="inventory-quantity" type="number" min="0" step="0.01" value={quantity} onChange={(event) => setQuantity(event.target.value)} required autoFocus />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="inventory-minimum">Minimum stock</Label>
              <Input id="inventory-minimum" type="number" min="0" step="0.01" value={minimumStock} onChange={(event) => setMinimumStock(event.target.value)} required />
            </div>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={updateMutation.isPending}>Cancel</Button>
            <Button type="submit" disabled={updateMutation.isPending}>{updateMutation.isPending ? "Saving..." : "Confirm adjustment"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
