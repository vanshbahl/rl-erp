import { useMemo, useState, type FormEvent } from "react"
import { Archive, Eye, Pencil, Plus, Search } from "lucide-react"
import { toast } from "sonner"
import { EmptyState } from "@/components/common/EmptyState"
import { PageHeader } from "@/components/common/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getApiErrorMessage } from "@/features/auth/api"

export interface MasterRecord {
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

type MasterPayload = Omit<MasterRecord, "id" | "is_active">
const FIELDS: Array<{ key: keyof MasterPayload; label: string; type?: string; wide?: boolean }> = [
  { key: "company_name", label: "Company name" }, { key: "contact_person", label: "Contact person" },
  { key: "phone", label: "Phone" }, { key: "email", label: "Email", type: "email" },
  { key: "gst_number", label: "GST number" }, { key: "city", label: "City" },
  { key: "state", label: "State" }, { key: "pincode", label: "Pincode" },
  { key: "address", label: "Address", wide: true },
]
const emptyPayload = (): MasterPayload => ({ company_name: "", contact_person: null, phone: null, email: null, gst_number: null, address: null, city: null, state: null, pincode: null })

interface Props<T extends MasterRecord> {
  title: string
  singular: string
  description: string
  records: T[] | undefined
  isLoading: boolean
  error: unknown
  refetch: () => unknown
  create: (payload: MasterPayload) => Promise<unknown>
  update: (id: number, payload: Partial<MasterPayload>) => Promise<unknown>
  deactivate: (id: number) => Promise<unknown>
  pending: boolean
}

export function MasterDataPage<T extends MasterRecord>({ title, singular, description, records, isLoading, error, refetch, create, update, deactivate, pending }: Props<T>) {
  const [search, setSearch] = useState("")
  const [formRecord, setFormRecord] = useState<T | null | undefined>(undefined)
  const [detailRecord, setDetailRecord] = useState<T | null>(null)
  const [deactivateRecord, setDeactivateRecord] = useState<T | null>(null)
  const [form, setForm] = useState<MasterPayload>(emptyPayload)
  const [formError, setFormError] = useState<string | null>(null)
  const filtered = useMemo(() => { const term = search.toLowerCase().trim(); return (records ?? []).filter((record) => !term || [record.company_name, record.contact_person, record.phone, record.email, record.city, record.state].filter(Boolean).some((value) => value!.toLowerCase().includes(term))) }, [records, search])
  const openCreate = () => { setForm(emptyPayload()); setFormError(null); setFormRecord(null) }
  const openEdit = (record: T) => { const { id, is_active, ...payload } = record; void id; void is_active; setForm(payload); setFormError(null); setFormRecord(record) }
  const save = async (event: FormEvent) => { event.preventDefault(); if (!form.company_name.trim()) { setFormError("Company name is required."); return } try { if (formRecord) await update(formRecord.id, form); else await create(form); toast.success(`${singular} ${formRecord ? "updated" : "created"}`); setFormRecord(undefined) } catch (requestError) { setFormError(getApiErrorMessage(requestError, `Unable to save ${singular.toLowerCase()}.`)) } }
  const setField = (key: keyof MasterPayload, value: string) => setForm((current) => ({ ...current, [key]: value.trim() ? value : null }))
  return <div className="space-y-5">
    <PageHeader title={title} description={description} actions={<Button onClick={openCreate}><Plus className="h-4 w-4" />New {singular}</Button>} />
    <Card className="overflow-hidden"><CardContent className="p-0">
      <div className="border-b border-border-subtle p-4"><div className="relative max-w-md"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input className="pl-9" value={search} onChange={(event) => setSearch(event.target.value)} placeholder={`Search ${title.toLowerCase()}...`} /></div></div>
      {isLoading ? <div className="space-y-2 p-4">{Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-10 w-full" />)}</div> : error ? <EmptyState title={`Unable to load ${title.toLowerCase()}.`} description={getApiErrorMessage(error, "Check the API connection and try again.")} action={<Button variant="outline" size="sm" onClick={() => void refetch()}>Try again</Button>} /> : filtered.length === 0 ? <EmptyState title={records?.length ? `No ${title.toLowerCase()} match this search.` : `No ${title.toLowerCase()} yet.`} description={records?.length ? "Adjust the search term." : `Create the first ${singular.toLowerCase()} to begin.`} action={!records?.length ? <Button size="sm" onClick={openCreate}><Plus className="h-4 w-4" />New {singular}</Button> : undefined} /> : <>
        <div className="hidden overflow-x-auto md:block"><Table><TableHeader><TableRow><TableHead>Company</TableHead><TableHead>Contact</TableHead><TableHead>Phone</TableHead><TableHead>Email</TableHead><TableHead>Location</TableHead><TableHead>GST</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader><TableBody>{filtered.map((record) => <TableRow key={record.id}><TableCell className="font-medium">{record.company_name}</TableCell><TableCell>{record.contact_person || "—"}</TableCell><TableCell>{record.phone || "—"}</TableCell><TableCell>{record.email || "—"}</TableCell><TableCell>{[record.city, record.state].filter(Boolean).join(", ") || "—"}</TableCell><TableCell>{record.gst_number || "—"}</TableCell><TableCell><Badge variant="secondary">Active</Badge></TableCell><TableCell><div className="flex justify-end gap-1"><Button variant="ghost" size="icon" onClick={() => setDetailRecord(record)} aria-label={`View ${record.company_name}`}><Eye className="h-4 w-4" /></Button><Button variant="ghost" size="icon" onClick={() => openEdit(record)} aria-label={`Edit ${record.company_name}`}><Pencil className="h-4 w-4" /></Button><Button variant="ghost" size="icon" onClick={() => setDeactivateRecord(record)} aria-label={`Deactivate ${record.company_name}`}><Archive className="h-4 w-4" /></Button></div></TableCell></TableRow>)}</TableBody></Table></div>
        <div className="divide-y divide-border-subtle md:hidden">{filtered.map((record) => <div key={record.id} className="space-y-3 p-4"><div className="flex justify-between gap-3"><div><p className="text-sm font-medium">{record.company_name}</p><p className="mt-0.5 text-xs text-muted-foreground">{record.contact_person || "No contact"} · {[record.city, record.state].filter(Boolean).join(", ") || "No location"}</p></div><Badge variant="secondary">Active</Badge></div><p className="text-xs text-muted-foreground">{record.phone || record.email || "No contact details"}</p><div className="flex gap-2"><Button variant="outline" size="sm" onClick={() => setDetailRecord(record)}>View</Button><Button variant="outline" size="sm" onClick={() => openEdit(record)}>Edit</Button><Button variant="ghost" size="sm" onClick={() => setDeactivateRecord(record)}>Deactivate</Button></div></div>)}</div>
      </>}
    </CardContent></Card>
    <Dialog open={formRecord !== undefined} onOpenChange={(open) => !open && setFormRecord(undefined)}><DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto"><DialogHeader><DialogTitle>{formRecord ? `Edit ${singular}` : `New ${singular}`}</DialogTitle><DialogDescription>Maintain the active {singular.toLowerCase()} master record.</DialogDescription></DialogHeader><form className="space-y-5" onSubmit={save}><div className="grid gap-4 sm:grid-cols-2">{FIELDS.map((field) => <div key={field.key} className={`space-y-1.5 ${field.wide ? "sm:col-span-2" : ""}`}><Label htmlFor={`${title}-${field.key}`}>{field.label}</Label>{field.key === "address" ? <textarea id={`${title}-${field.key}`} className="min-h-20 w-full resize-y rounded-md border border-input bg-card px-3 py-2 text-sm focus-visible:border-primary/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/15" value={form[field.key] ?? ""} onChange={(event) => setField(field.key, event.target.value)} /> : <Input id={`${title}-${field.key}`} type={field.type} required={field.key === "company_name"} value={form[field.key] ?? ""} onChange={(event) => setField(field.key, event.target.value)} />}</div>)}</div>{formError && <p className="text-sm text-destructive">{formError}</p>}<DialogFooter><Button type="button" variant="outline" onClick={() => setFormRecord(undefined)} disabled={pending}>Cancel</Button><Button type="submit" disabled={pending}>{pending ? "Saving..." : "Save"}</Button></DialogFooter></form></DialogContent></Dialog>
    <Dialog open={Boolean(detailRecord)} onOpenChange={(open) => !open && setDetailRecord(null)}><DialogContent><DialogHeader><DialogTitle>{detailRecord?.company_name}</DialogTitle><DialogDescription>{detailRecord?.contact_person || "No contact person"}</DialogDescription></DialogHeader><div className="grid gap-2 sm:grid-cols-2">{FIELDS.map((field) => <div key={field.key} className={`rounded-md bg-secondary/65 p-3 ${field.wide ? "sm:col-span-2" : ""}`}><p className="text-[11px] text-muted-foreground">{field.label}</p><p className="mt-1 text-sm">{detailRecord?.[field.key] || "Not set"}</p></div>)}</div></DialogContent></Dialog>
    <Dialog open={Boolean(deactivateRecord)} onOpenChange={(open) => !open && setDeactivateRecord(null)}><DialogContent><DialogHeader><DialogTitle>Deactivate {singular.toLowerCase()}?</DialogTitle><DialogDescription>{deactivateRecord?.company_name} will be hidden from active selectors while historical records remain preserved.</DialogDescription></DialogHeader><DialogFooter><Button variant="outline" onClick={() => setDeactivateRecord(null)} disabled={pending}>Cancel</Button><Button variant="destructive" disabled={pending} onClick={() => { if (!deactivateRecord) return; void deactivate(deactivateRecord.id).then(() => { toast.success(`${singular} deactivated`); setDeactivateRecord(null) }).catch((requestError) => toast.error(getApiErrorMessage(requestError, `Unable to deactivate ${singular.toLowerCase()}.`))) }}>{pending ? "Deactivating..." : "Deactivate"}</Button></DialogFooter></DialogContent></Dialog>
  </div>
}
