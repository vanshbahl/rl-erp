import type { ProductType } from "@/features/products/types"

export interface InventoryItem {
  id: number
  product_id: number
  quantity: number
  minimum_stock: number
}

export interface InventoryUpdatePayload {
  quantity?: number
  minimum_stock?: number
}

export interface LowStockParams {
  productType?: ProductType
  supplierId?: number
}

export type StockStatus = "Healthy" | "Low Stock" | "Out of Stock"

export function getStockStatus(item: InventoryItem): StockStatus {
  if (item.quantity <= 0) return "Out of Stock"
  if (item.quantity <= item.minimum_stock) return "Low Stock"
  return "Healthy"
}
