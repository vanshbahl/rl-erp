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
  Boxes,
  Package,
  Search,
  LogOut,
} from "lucide-react"
import { useAuthStore } from "@/stores/auth.store"

interface CommandRoute {
  label: string
  icon: React.ComponentType<{ className?: string }>
  path: string
}

const ROUTES: CommandRoute[] = [
  { label: "Dashboard", icon: LayoutDashboard, path: "/app/dashboard" },
  { label: "Products", icon: Package, path: "/app/products" },
  { label: "Inventory", icon: Boxes, path: "/app/inventory" },
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
    navigate("/login", { replace: true })
  }, [logout, navigate])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search pages, actions..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Navigation">
          {ROUTES.map((route) => (
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
