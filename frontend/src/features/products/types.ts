export const PRODUCT_TYPES = [
  "RAW_MATERIAL",
  "FINISHED_GOOD",
  "SEMI_FINISHED",
  "PACKAGING",
  "CONSUMABLE",
] as const

export type ProductType = (typeof PRODUCT_TYPES)[number]

export interface Product {
  id: number
  name: string
  sku: string
  hsn_code: string | null
  gst_rate: number | null
  unit: string | null
  base_price: number | null
  color: string | null
  description: string | null
  product_type: ProductType
  standard_cost: number | string
  default_supplier_id: number | null
  is_active: boolean
}

export interface ProductPayload {
  name: string
  sku: string
  hsn_code?: string | null
  gst_rate?: number | null
  unit?: string | null
  base_price?: number | null
  color?: string | null
  description?: string | null
  product_type: ProductType
  standard_cost: number
}

export interface DeactivateProductResponse {
  message: string
  product: Product
}

export function formatProductType(productType: ProductType): string {
  return productType
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}
