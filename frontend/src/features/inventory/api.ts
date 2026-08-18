import { api } from "@/lib/axios"
import type {
  InventoryItem,
  InventoryUpdatePayload,
  LowStockParams,
} from "@/features/inventory/types"

export const inventoryApi = {
  async list(): Promise<InventoryItem[]> {
    const { data } = await api.get<InventoryItem[]>("/inventory/")
    return data
  },

  async lowStock(params: LowStockParams = {}): Promise<InventoryItem[]> {
    const { data } = await api.get<InventoryItem[]>("/inventory/low-stock", {
      params: {
        product_type: params.productType,
        supplier_id: params.supplierId,
      },
    })
    return data
  },

  async get(productId: number): Promise<InventoryItem> {
    const { data } = await api.get<InventoryItem>(`/inventory/${productId}`)
    return data
  },

  async update(
    productId: number,
    payload: InventoryUpdatePayload,
  ): Promise<InventoryItem> {
    const { data } = await api.put<InventoryItem>(
      `/inventory/${productId}`,
      payload,
    )
    return data
  },
}
