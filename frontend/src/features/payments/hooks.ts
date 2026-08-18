import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { invoiceKeys } from "@/features/invoices/hooks"
import { paymentsApi } from "@/features/payments/api"
import type { PaymentPayload } from "@/features/payments/types"
export const paymentKeys = { all: ["payments"] as const, list: () => [...paymentKeys.all, "list"] as const, outstanding: () => [...paymentKeys.all, "outstanding"] as const, invoiceSummary: (id: number) => [...paymentKeys.all, "invoice-summary", id] as const }
export function usePaymentsQuery() { return useQuery({ queryKey: paymentKeys.list(), queryFn: paymentsApi.list }) }
export function useOutstandingQuery() { return useQuery({ queryKey: paymentKeys.outstanding(), queryFn: paymentsApi.outstanding }) }
export function useInvoicePaymentSummaryQuery(id: number | null) { return useQuery({ queryKey: paymentKeys.invoiceSummary(id ?? 0), queryFn: () => paymentsApi.invoiceSummary(id as number), enabled: id !== null }) }
export function useCreatePaymentMutation() { const queryClient = useQueryClient(); return useMutation({ mutationFn: (payload: PaymentPayload) => paymentsApi.create(payload), onSuccess: (_, variables) => { void queryClient.invalidateQueries({ queryKey: paymentKeys.all }); void queryClient.invalidateQueries({ queryKey: invoiceKeys.all }); void queryClient.invalidateQueries({ queryKey: invoiceKeys.detail(variables.invoice_id) }) } }) }
