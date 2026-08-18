import { api } from "@/lib/axios"
import type { InvoicePaymentSummary, OutstandingInvoice, Payment, PaymentPayload } from "@/features/payments/types"
export const paymentsApi = {
  async list(): Promise<Payment[]> { return (await api.get<Payment[]>("/payments")).data },
  async create(payload: PaymentPayload): Promise<Payment> { return (await api.post<Payment>("/payments", payload)).data },
  async invoiceSummary(invoiceId: number): Promise<InvoicePaymentSummary> { return (await api.get<InvoicePaymentSummary>(`/payments/invoice/${invoiceId}/summary`)).data },
  async outstanding(): Promise<OutstandingInvoice[]> { return (await api.get<OutstandingInvoice[]>("/payments/outstanding")).data },
}
