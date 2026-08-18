import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { suppliersApi } from "@/features/suppliers/api"
import type { SupplierPayload } from "@/features/suppliers/types"

export const supplierKeys = { all: ["suppliers"] as const, list: () => [...supplierKeys.all, "list"] as const, detail: (id: number) => [...supplierKeys.all, "detail", id] as const }
export function useSuppliersQuery() { return useQuery({ queryKey: supplierKeys.list(), queryFn: suppliersApi.list }) }
export function useSupplierDetailQuery(id: number | null) { return useQuery({ queryKey: supplierKeys.detail(id ?? 0), queryFn: () => suppliersApi.get(id as number), enabled: id !== null }) }
function useSupplierMutation<T>(mutationFn: (variables: T) => Promise<unknown>) { const queryClient = useQueryClient(); return useMutation({ mutationFn, onSuccess: () => { void queryClient.invalidateQueries({ queryKey: supplierKeys.all }) } }) }
export function useCreateSupplierMutation() { return useSupplierMutation((payload: SupplierPayload) => suppliersApi.create(payload)) }
export function useUpdateSupplierMutation() { return useSupplierMutation(({ id, payload }: { id: number; payload: Partial<SupplierPayload> }) => suppliersApi.update(id, payload)) }
export function useDeactivateSupplierMutation() { return useSupplierMutation((id: number) => suppliersApi.deactivate(id)) }
