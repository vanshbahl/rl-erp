export interface Supplier {
  id: number
  company_name: string
  contact_person: string | null
  phone: string | null
  email: string | null
  gst_number: string | null
  address: string | null
  city: string | null
  state: string | null
  pincode: string | null
  is_active: boolean
}

export type SupplierPayload = Omit<Supplier, "id" | "is_active">
