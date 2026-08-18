import { api } from "@/lib/axios"
import type { Order, OrderCreatePayload, OrderDetail, OrderStatus } from "@/features/orders/types"
export const ordersApi = {
  async list(): Promise<Order[]> { return (await api.get<Order[]>("/orders/")).data },
  async get(id: number): Promise<OrderDetail> { return (await api.get<OrderDetail>(`/orders/${id}`)).data },
  async create(payload: OrderCreatePayload): Promise<{ order_id: number }> { return (await api.post<{ order_id: number }>("/orders/", payload)).data },
  async updateStatus(id: number, status: OrderStatus): Promise<{ order_id: number; status: OrderStatus }> { return (await api.patch<{ order_id: number; status: OrderStatus }>(`/orders/${id}/status`, { status })).data },
}
