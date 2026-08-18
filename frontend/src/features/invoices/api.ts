import { api } from "@/lib/axios"
import type { Invoice, InvoiceDetail, InvoiceStatus } from "@/features/invoices/types"
export const invoicesApi = {
  async list(): Promise<Invoice[]> { return (await api.get<Invoice[]>("/invoices")).data },
  async get(id: number): Promise<InvoiceDetail> { return (await api.get<InvoiceDetail>(`/invoices/${id}`)).data },
  async generate(orderId: number): Promise<{ invoice_id: number; invoice_number: string }> { return (await api.post<{ invoice_id: number; invoice_number: string }>(`/invoices/generate/${orderId}`)).data },
  async updateStatus(id: number, status: InvoiceStatus): Promise<{ invoice: Invoice }> { return (await api.patch<{ invoice: Invoice }>(`/invoices/${id}/status`, { status })).data },
}
