import { api } from "@/lib/axios"
import type { Supplier, SupplierPayload } from "@/features/suppliers/types"

export const suppliersApi = {
  async list(): Promise<Supplier[]> { return (await api.get<Supplier[]>("/suppliers")).data },
  async get(id: number): Promise<Supplier> { return (await api.get<Supplier>(`/suppliers/${id}`)).data },
  async create(payload: SupplierPayload): Promise<Supplier> { return (await api.post<Supplier>("/suppliers", payload)).data },
  async update(id: number, payload: Partial<SupplierPayload>): Promise<Supplier> { return (await api.put<Supplier>(`/suppliers/${id}`, payload)).data },
  async deactivate(id: number): Promise<{ message: string }> { return (await api.delete<{ message: string }>(`/suppliers/${id}`)).data },
}
