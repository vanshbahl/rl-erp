import { useState, useCallback, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import {
  LayoutDashboard,
  Package,
  Users,
  Truck,
  ShoppingCart,
  FileText,
  BarChart3,
  Settings,
  Search,
  LogOut,
} from "lucide-react"
import { useAuthStore } from "@/stores/auth.store"

interface CommandRoute {
  label: string
  icon: React.ComponentType<{ className?: string }>
  path: string
  group: "navigation" | "actions"
}

const ROUTES: CommandRoute[] = [
  { label: "Dashboard", icon: LayoutDashboard, path: "/app/dashboard", group: "navigation" },
  { label: "Products", icon: Package, path: "/app/products", group: "navigation" },
  { label: "Customers", icon: Users, path: "/app/customers", group: "navigation" },
  { label: "Suppliers", icon: Truck, path: "/app/suppliers", group: "navigation" },
  { label: "Sales Orders", icon: ShoppingCart, path: "/app/sales", group: "navigation" },
  { label: "Purchase Orders", icon: FileText, path: "/app/purchases", group: "navigation" },
  { label: "Inventory", icon: Package, path: "/app/inventory", group: "navigation" },
  { label: "Invoices", icon: FileText, path: "/app/invoices", group: "navigation" },
  { label: "Reports", icon: BarChart3, path: "/app/reports", group: "navigation" },
  { label: "Settings", icon: Settings, path: "/app/settings", group: "actions" },
]

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setOpen((prev) => !prev)
      }
    }
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [])

  const handleSelect = useCallback(
    (path: string) => {
      setOpen(false)
      navigate(path)
    },
    [navigate],
  )

  const handleLogout = useCallback(() => {
    setOpen(false)
    logout()
    navigate("/")
  }, [logout, navigate])

  const navRoutes = ROUTES.filter((r) => r.group === "navigation")
  const actionRoutes = ROUTES.filter((r) => r.group === "actions")

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search pages, actions..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Navigation">
          {navRoutes.map((route) => (
            <CommandItem
              key={route.path}
              onSelect={() => handleSelect(route.path)}
              className="gap-3"
            >
              <route.icon className="h-4 w-4 text-muted-foreground" />
              <span>{route.label}</span>
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Actions">
          {actionRoutes.map((route) => (
            <CommandItem
              key={route.path}
              onSelect={() => handleSelect(route.path)}
              className="gap-3"
            >
              <route.icon className="h-4 w-4 text-muted-foreground" />
              <span>{route.label}</span>
            </CommandItem>
          ))}
          <CommandItem onSelect={handleLogout} className="gap-3">
            <LogOut className="h-4 w-4 text-muted-foreground" />
            <span>Log out</span>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <div className="px-3 py-2 text-xs text-muted-foreground flex items-center gap-1.5">
          <Search className="h-3 w-3" />
          <span>⌘K to toggle • Type to search</span>
        </div>
      </CommandList>
    </CommandDialog>
  )
}
