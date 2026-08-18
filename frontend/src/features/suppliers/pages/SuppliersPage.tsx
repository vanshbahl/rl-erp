import { MasterDataPage } from "@/features/master-data/MasterDataPage"
import { useCreateSupplierMutation, useDeactivateSupplierMutation, useSuppliersQuery, useUpdateSupplierMutation } from "@/features/suppliers/hooks"

export default function SuppliersPage() {
  const query = useSuppliersQuery(); const create = useCreateSupplierMutation(); const update = useUpdateSupplierMutation(); const deactivate = useDeactivateSupplierMutation()
  return <MasterDataPage title="Suppliers" singular="Supplier" description="Manage active supplier master data for future procurement workflows." records={query.data} isLoading={query.isLoading} error={query.error} refetch={query.refetch} create={(payload) => create.mutateAsync(payload)} update={(id, payload) => update.mutateAsync({ id, payload })} deactivate={(id) => deactivate.mutateAsync(id)} pending={create.isPending || update.isPending || deactivate.isPending} />
}
