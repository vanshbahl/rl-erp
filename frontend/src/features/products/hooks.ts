import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { inventoryKeys } from "@/features/inventory/hooks"
import { productsApi } from "@/features/products/api"
import type { ProductPayload } from "@/features/products/types"

export const productKeys = {
  all: ["products"] as const,
  list: () => [...productKeys.all, "list"] as const,
  detail: (productId: number) =>
    [...productKeys.all, "detail", productId] as const,
}

export function useProductsQuery() {
  return useQuery({
    queryKey: productKeys.list(),
    queryFn: productsApi.list,
  })
}

export function useProductDetailQuery(productId: number | null) {
  return useQuery({
    queryKey: productKeys.detail(productId ?? 0),
    queryFn: () => productsApi.get(productId as number),
    enabled: productId !== null,
  })
}

export function useCreateProductMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: productsApi.create,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: productKeys.all })
      void queryClient.invalidateQueries({ queryKey: inventoryKeys.all })
    },
  })
}

export function useUpdateProductMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      productId,
      payload,
    }: {
      productId: number
      payload: ProductPayload
    }) => productsApi.update(productId, payload),
    onSuccess: (product) => {
      queryClient.setQueryData(productKeys.detail(product.id), product)
      void queryClient.invalidateQueries({ queryKey: productKeys.list() })
    },
  })
}

export function useDeactivateProductMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: productsApi.deactivate,
    onSuccess: ({ product }) => {
      queryClient.setQueryData(productKeys.detail(product.id), product)
      void queryClient.invalidateQueries({ queryKey: productKeys.list() })
      void queryClient.invalidateQueries({ queryKey: inventoryKeys.all })
    },
  })
}
