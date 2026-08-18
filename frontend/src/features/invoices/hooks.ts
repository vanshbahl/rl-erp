import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { invoicesApi } from "@/features/invoices/api"
import type { InvoiceStatus } from "@/features/invoices/types"
export const invoiceKeys = { all: ["invoices"] as const, list: () => [...invoiceKeys.all, "list"] as const, detail: (id: number) => [...invoiceKeys.all, "detail", id] as const }
export function useInvoicesQuery() { return useQuery({ queryKey: invoiceKeys.list(), queryFn: invoicesApi.list }) }
export function useInvoiceDetailQuery(id: number | null) { return useQuery({ queryKey: invoiceKeys.detail(id ?? 0), queryFn: () => invoicesApi.get(id as number), enabled: id !== null }) }
export function useGenerateInvoiceMutation() { const queryClient = useQueryClient(); return useMutation({ mutationFn: invoicesApi.generate, onSuccess: () => void queryClient.invalidateQueries({ queryKey: invoiceKeys.all }) }) }
export function useInvoiceStatusMutation() { const queryClient = useQueryClient(); return useMutation({ mutationFn: ({ id, status }: { id: number; status: InvoiceStatus }) => invoicesApi.updateStatus(id, status), onSuccess: (_, variables) => { void queryClient.invalidateQueries({ queryKey: invoiceKeys.all }); void queryClient.invalidateQueries({ queryKey: invoiceKeys.detail(variables.id) }) } }) }
