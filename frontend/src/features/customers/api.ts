import { api } from "@/lib/axios"
import type { Customer, CustomerPayload } from "@/features/customers/types"

export const customersApi = {
  async list(): Promise<Customer[]> { return (await api.get<Customer[]>("/customers/")).data },
  async get(id: number): Promise<Customer> { return (await api.get<Customer>(`/customers/${id}`)).data },
  async create(payload: CustomerPayload): Promise<Customer> { return (await api.post<Customer>("/customers/", payload)).data },
  async update(id: number, payload: Partial<CustomerPayload>): Promise<Customer> { return (await api.put<Customer>(`/customers/${id}`, payload)).data },
  async deactivate(id: number): Promise<{ message: string; customer: Customer }> { return (await api.patch<{ message: string; customer: Customer }>(`/customers/${id}/deactivate`)).data },
}
