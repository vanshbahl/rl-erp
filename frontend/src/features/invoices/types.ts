export const INVOICE_STATUSES = ["DRAFT", "ISSUED", "PARTIALLY_PAID", "PAID", "CANCELLED"] as const
export type InvoiceStatus = (typeof INVOICE_STATUSES)[number]
export interface Invoice { id: number; invoice_number: string; order_id: number; customer_id: number; subtotal: number | string; tax_amount: number | string; total_amount: number | string; status: InvoiceStatus; created_at: string }
export interface InvoiceItem { id?: number; product_id: number; quantity: number; rate: number | string; amount: number | string }
export interface InvoiceDetail { invoice: Invoice; items: InvoiceItem[] }
export const formatInvoiceStatus = (status: string) => status.toLowerCase().replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())
