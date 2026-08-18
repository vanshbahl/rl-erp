import { api } from "@/lib/axios"
import type {
  DeactivateProductResponse,
  Product,
  ProductPayload,
} from "@/features/products/types"

export const productsApi = {
  async list(): Promise<Product[]> {
    const { data } = await api.get<Product[]>("/products/")
    return data
  },

  async get(productId: number): Promise<Product> {
    const { data } = await api.get<Product>(`/products/${productId}`)
    return data
  },

  async create(payload: ProductPayload): Promise<Product> {
    const { data } = await api.post<Product>("/products/", payload)
    return data
  },

  async update(productId: number, payload: ProductPayload): Promise<Product> {
    const { data } = await api.put<Product>(`/products/${productId}`, payload)
    return data
  },

  async deactivate(productId: number): Promise<DeactivateProductResponse> {
    const { data } = await api.patch<DeactivateProductResponse>(
      `/products/${productId}/deactivate`,
    )
    return data
  },
}
