export const PAYMENT_METHODS = ["CASH", "BANK_TRANSFER", "CHEQUE", "UPI", "CARD"] as const
export type PaymentMethod = (typeof PAYMENT_METHODS)[number]
export interface Payment { id: number; invoice_id: number; amount: number | string; payment_method: PaymentMethod; reference_number: string | null; remarks: string | null; payment_date: string; created_at: string }
export interface PaymentPayload { invoice_id: number; amount: number; payment_method: PaymentMethod; reference_number?: string | null; remarks?: string | null }
export interface InvoicePaymentSummary { invoice_id: number; invoice_total: number; paid_amount: number; outstanding_amount: number; status: string }
export interface OutstandingInvoice { customer_id: number; company_name: string; invoice_id: number; invoice_number: string; invoice_total: number; paid_amount: number; outstanding_amount: number; status: string }
