import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { customersApi } from "@/features/customers/api"
import type { CustomerPayload } from "@/features/customers/types"

export const customerKeys = { all: ["customers"] as const, list: () => [...customerKeys.all, "list"] as const, detail: (id: number) => [...customerKeys.all, "detail", id] as const }
export function useCustomersQuery() { return useQuery({ queryKey: customerKeys.list(), queryFn: customersApi.list }) }
export function useCustomerDetailQuery(id: number | null) { return useQuery({ queryKey: customerKeys.detail(id ?? 0), queryFn: () => customersApi.get(id as number), enabled: id !== null }) }
function useCustomerMutation<T>(mutationFn: (variables: T) => Promise<unknown>) { const queryClient = useQueryClient(); return useMutation({ mutationFn, onSuccess: () => { void queryClient.invalidateQueries({ queryKey: customerKeys.all }) } }) }
export function useCreateCustomerMutation() { return useCustomerMutation((payload: CustomerPayload) => customersApi.create(payload)) }
export function useUpdateCustomerMutation() { return useCustomerMutation(({ id, payload }: { id: number; payload: Partial<CustomerPayload> }) => customersApi.update(id, payload)) }
export function useDeactivateCustomerMutation() { return useCustomerMutation((id: number) => customersApi.deactivate(id)) }
