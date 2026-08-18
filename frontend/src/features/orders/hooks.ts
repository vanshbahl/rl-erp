import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { invoiceKeys } from "@/features/invoices/hooks"
import { inventoryKeys } from "@/features/inventory/hooks"
import { ordersApi } from "@/features/orders/api"
import type { OrderCreatePayload, OrderStatus } from "@/features/orders/types"
export const orderKeys = { all: ["orders"] as const, list: () => [...orderKeys.all, "list"] as const, detail: (id: number) => [...orderKeys.all, "detail", id] as const }
export function useOrdersQuery() { return useQuery({ queryKey: orderKeys.list(), queryFn: ordersApi.list }) }
export function useOrderDetailQuery(id: number | null) { return useQuery({ queryKey: orderKeys.detail(id ?? 0), queryFn: () => ordersApi.get(id as number), enabled: id !== null }) }
export function useCreateOrderMutation() { const queryClient = useQueryClient(); return useMutation({ mutationFn: (payload: OrderCreatePayload) => ordersApi.create(payload), onSuccess: () => void queryClient.invalidateQueries({ queryKey: orderKeys.all }) }) }
export function useOrderStatusMutation() { const queryClient = useQueryClient(); return useMutation({ mutationFn: ({ id, status }: { id: number; status: OrderStatus }) => ordersApi.updateStatus(id, status), onSuccess: (_, variables) => { void queryClient.invalidateQueries({ queryKey: orderKeys.all }); void queryClient.invalidateQueries({ queryKey: inventoryKeys.all }); void queryClient.invalidateQueries({ queryKey: invoiceKeys.all }); void queryClient.invalidateQueries({ queryKey: orderKeys.detail(variables.id) }) } }) }
