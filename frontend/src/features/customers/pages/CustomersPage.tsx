import { MasterDataPage } from "@/features/master-data/MasterDataPage"
import { useCreateCustomerMutation, useCustomersQuery, useDeactivateCustomerMutation, useUpdateCustomerMutation } from "@/features/customers/hooks"

export default function CustomersPage() {
  const query = useCustomersQuery(); const create = useCreateCustomerMutation(); const update = useUpdateCustomerMutation(); const deactivate = useDeactivateCustomerMutation()
  return <MasterDataPage title="Customers" singular="Customer" description="Manage active customer master data for sales and invoicing." records={query.data} isLoading={query.isLoading} error={query.error} refetch={query.refetch} create={(payload) => create.mutateAsync(payload)} update={(id, payload) => update.mutateAsync({ id, payload })} deactivate={(id) => deactivate.mutateAsync(id)} pending={create.isPending || update.isPending || deactivate.isPending} />
}
