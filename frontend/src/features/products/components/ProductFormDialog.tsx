import { useState, type FormEvent } from "react"
import { toast } from "sonner"
import { getApiErrorMessage } from "@/features/auth/api"
import {
  useCreateProductMutation,
  useUpdateProductMutation,
} from "@/features/products/hooks"
import {
  PRODUCT_TYPES,
  formatProductType,
  type Product,
  type ProductPayload,
  type ProductType,
} from "@/features/products/types"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface ProductFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  product?: Product | null
}

interface ProductFormState {
  name: string
  sku: string
  productType: ProductType
  unit: string
  hsnCode: string
  gstRate: string
  basePrice: string
  standardCost: string
  color: string
  description: string
}

const EMPTY_FORM: ProductFormState = {
  name: "",
  sku: "",
  productType: "FINISHED_GOOD",
  unit: "",
  hsnCode: "",
  gstRate: "",
  basePrice: "",
  standardCost: "0",
  color: "",
  description: "",
}

function getInitialForm(product?: Product | null): ProductFormState {
  return product
    ? {
        name: product.name,
        sku: product.sku,
        productType: product.product_type,
        unit: product.unit ?? "",
        hsnCode: product.hsn_code ?? "",
        gstRate: product.gst_rate?.toString() ?? "",
        basePrice: product.base_price?.toString() ?? "",
        standardCost: product.standard_cost?.toString() ?? "0",
        color: product.color ?? "",
        description: product.description ?? "",
      }
    : EMPTY_FORM
}

function optionalNumber(value: string): number | null {
  return value.trim() === "" ? null : Number(value)
}

export function ProductFormDialog({
  open,
  onOpenChange,
  product,
}: ProductFormDialogProps) {
  const createMutation = useCreateProductMutation()
  const updateMutation = useUpdateProductMutation()
  const [form, setForm] = useState<ProductFormState>(() => getInitialForm(product))
  const [validationError, setValidationError] = useState<string | null>(null)
  const isEditing = Boolean(product)
  const isPending = createMutation.isPending || updateMutation.isPending

  const updateField = <K extends keyof ProductFormState>(
    field: K,
    value: ProductFormState[K],
  ) => setForm((current) => ({ ...current, [field]: value }))

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setValidationError(null)

    if (!form.name.trim() || !form.sku.trim()) {
      setValidationError("Product name and SKU are required.")
      return
    }

    const gstRate = optionalNumber(form.gstRate)
    const basePrice = optionalNumber(form.basePrice)
    const standardCost = Number(form.standardCost || 0)

    if (
      [gstRate, basePrice, standardCost].some(
        (value) => value !== null && (!Number.isFinite(value) || value < 0),
      )
    ) {
      setValidationError("Rates and costs must be valid non-negative numbers.")
      return
    }

    const payload: ProductPayload = {
      name: form.name.trim(),
      sku: form.sku.trim(),
      product_type: form.productType,
      unit: form.unit.trim() || null,
      hsn_code: form.hsnCode.trim() || null,
      gst_rate: gstRate,
      base_price: basePrice,
      standard_cost: standardCost,
      color: form.color.trim() || null,
      description: form.description.trim() || null,
    }

    try {
      if (product) {
        await updateMutation.mutateAsync({ productId: product.id, payload })
        toast.success("Product updated")
      } else {
        await createMutation.mutateAsync(payload)
        toast.success("Product created")
      }
      onOpenChange(false)
    } catch (error) {
      setValidationError(
        getApiErrorMessage(
          error,
          isEditing ? "Unable to update product." : "Unable to create product.",
        ),
      )
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Product" : "New Product"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Update the product master data supported by the current API."
              : "Create a product and its initial inventory record."}
          </DialogDescription>
        </DialogHeader>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="product-name">Product name</Label>
              <Input id="product-name" value={form.name} onChange={(event) => updateField("name", event.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="product-sku">SKU</Label>
              <Input id="product-sku" value={form.sku} onChange={(event) => updateField("sku", event.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label>Product type</Label>
              <Select value={form.productType} onValueChange={(value) => updateField("productType", value as ProductType)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {PRODUCT_TYPES.map((productType) => (
                    <SelectItem key={productType} value={productType}>{formatProductType(productType)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="product-unit">Unit</Label>
              <Input id="product-unit" placeholder="kg, pcs, roll..." value={form.unit} onChange={(event) => updateField("unit", event.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="product-hsn">HSN code</Label>
              <Input id="product-hsn" value={form.hsnCode} onChange={(event) => updateField("hsnCode", event.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="product-gst">GST rate (%)</Label>
              <Input id="product-gst" type="number" min="0" step="1" value={form.gstRate} onChange={(event) => updateField("gstRate", event.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="product-price">Base price</Label>
              <Input id="product-price" type="number" min="0" step="1" value={form.basePrice} onChange={(event) => updateField("basePrice", event.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="product-cost">Standard cost</Label>
              <Input id="product-cost" type="number" min="0" step="0.01" value={form.standardCost} onChange={(event) => updateField("standardCost", event.target.value)} />
            </div>
            <div className="space-y-1.5 sm:col-span-2">
              <Label htmlFor="product-color">Color</Label>
              <Input id="product-color" value={form.color} onChange={(event) => updateField("color", event.target.value)} />
            </div>
            <div className="space-y-1.5 sm:col-span-2">
              <Label htmlFor="product-description">Description</Label>
              <textarea
                id="product-description"
                className="min-h-20 w-full resize-y rounded-md border border-input bg-card px-3 py-2 text-sm placeholder:text-muted-foreground/75 focus-visible:border-primary/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/15"
                value={form.description}
                onChange={(event) => updateField("description", event.target.value)}
              />
            </div>
          </div>

          {validationError && <p className="text-sm text-destructive">{validationError}</p>}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isPending}>Cancel</Button>
            <Button type="submit" disabled={isPending}>{isPending ? "Saving..." : isEditing ? "Save changes" : "Create product"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
