export interface Customer {
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

export type CustomerPayload = Omit<Customer, "id" | "is_active">
