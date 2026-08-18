export const ORDER_STATUSES = ["PENDING", "PROCESSING", "DISPATCHED", "COMPLETED", "CANCELLED"] as const
export type OrderStatus = (typeof ORDER_STATUSES)[number]
export interface Order { id: number; customer_id: number; contact_person: string; po_number: string | null; remarks: string | null; status: OrderStatus; total_amount: number | string; order_date: string }
export interface OrderItem { id?: number; product_id: number; quantity: number; rate: number | string; amount: number | string }
export interface OrderDetail { order_id: number; customer_id: number; status: OrderStatus; total_amount: number | string; items: OrderItem[] }
export interface OrderCreatePayload { customer_id: number; contact_person: string; po_number?: string | null; remarks?: string | null; items: Array<{ product_id: number; quantity: number; rate: number }> }
export const formatOrderStatus = (status: string) => status.toLowerCase().replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())
