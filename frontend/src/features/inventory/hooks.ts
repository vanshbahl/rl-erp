import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { inventoryApi } from "@/features/inventory/api"
import type {
  InventoryUpdatePayload,
  LowStockParams,
} from "@/features/inventory/types"

export const inventoryKeys = {
  all: ["inventory"] as const,
  list: () => [...inventoryKeys.all, "list"] as const,
  lowStock: (params: LowStockParams = {}) =>
    [...inventoryKeys.all, "low-stock", params] as const,
  detail: (productId: number) =>
    [...inventoryKeys.all, "detail", productId] as const,
}

export function useInventoryQuery() {
  return useQuery({
    queryKey: inventoryKeys.list(),
    queryFn: inventoryApi.list,
  })
}

export function useLowStockQuery(params: LowStockParams = {}) {
  return useQuery({
    queryKey: inventoryKeys.lowStock(params),
    queryFn: () => inventoryApi.lowStock(params),
  })
}

export function useInventoryDetailQuery(productId: number | null) {
  return useQuery({
    queryKey: inventoryKeys.detail(productId ?? 0),
    queryFn: () => inventoryApi.get(productId as number),
    enabled: productId !== null,
  })
}

export function useUpdateInventoryMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      productId,
      payload,
    }: {
      productId: number
      payload: InventoryUpdatePayload
    }) => inventoryApi.update(productId, payload),
    onSuccess: (inventory) => {
      queryClient.setQueryData(inventoryKeys.detail(inventory.product_id), inventory)
      void queryClient.invalidateQueries({ queryKey: inventoryKeys.all })
    },
  })
}
