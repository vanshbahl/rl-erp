import { useState } from "react"
import { Outlet, NavLink, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { CommandPalette } from "@/components/common/CommandPalette"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import {
  LayoutDashboard,
  Package,
  Users,
  Truck,
  ShoppingCart,
  FileText,
  BarChart3,
  Settings,
  Menu,
  Search,
  ChevronsLeft,
  ChevronsRight,
  Boxes,
  Receipt,
} from "lucide-react"
import { useAuthStore } from "@/stores/auth.store"

interface NavItem {
  label: string
  icon: React.ComponentType<{ className?: string }>
  path: string
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", icon: LayoutDashboard, path: "/app/dashboard" },
  { label: "Products", icon: Package, path: "/app/products" },
  { label: "Customers", icon: Users, path: "/app/customers" },
  { label: "Suppliers", icon: Truck, path: "/app/suppliers" },
  { label: "Purchase Orders", icon: FileText, path: "/app/purchases" },
  { label: "Sales Orders", icon: ShoppingCart, path: "/app/sales" },
  { label: "Inventory", icon: Boxes, path: "/app/inventory" },
  { label: "Invoices", icon: Receipt, path: "/app/invoices" },
  { label: "Reports", icon: BarChart3, path: "/app/reports" },
]

const BOTTOM_NAV: NavItem[] = [
  { label: "Settings", icon: Settings, path: "/app/settings" },
]

function SidebarContent({
  collapsed,
  onToggle,
}: {
  collapsed: boolean
  onToggle: () => void
}) {
  const user = useAuthStore((s) => s.user)
  const location = useLocation()

  const renderNavItem = (item: NavItem) => {
    const isActive = location.pathname === item.path
    const link = (
      <NavLink
        key={item.path}
        to={item.path}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
          "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
          isActive
            ? "bg-sidebar-accent text-sidebar-primary"
            : "text-sidebar-foreground/70",
          collapsed && "justify-center px-2",
        )}
      >
        <item.icon className="h-4 w-4 shrink-0" />
        {!collapsed && <span>{item.label}</span>}
      </NavLink>
    )

    if (collapsed) {
      return (
        <Tooltip key={item.path}>
          <TooltipTrigger asChild>{link}</TooltipTrigger>
          <TooltipContent side="right" className="text-xs">
            {item.label}
          </TooltipContent>
        </Tooltip>
      )
    }
    return link
  }

  return (
    <div className="flex h-full flex-col bg-sidebar">
      {/* Logo area */}
      <div
        className={cn(
          "flex h-14 items-center border-b border-sidebar-border px-4",
          collapsed && "justify-center px-2",
        )}
      >
        {!collapsed ? (
          <span className="text-base font-semibold tracking-tight text-sidebar-foreground">
            RL-ERP
          </span>
        ) : (
          <span className="text-base font-bold text-sidebar-primary">R</span>
        )}
      </div>

      {/* Main nav */}
      <ScrollArea className="flex-1 px-3 py-3">
        <nav className="flex flex-col gap-1">{NAV_ITEMS.map(renderNavItem)}</nav>
      </ScrollArea>

      {/* Bottom section */}
      <div className="border-t border-sidebar-border px-3 py-3">
        <nav className="flex flex-col gap-1">{BOTTOM_NAV.map(renderNavItem)}</nav>
        <Separator className="my-2 bg-sidebar-border" />

        {/* User + collapse toggle */}
        <div className={cn("flex items-center", collapsed ? "justify-center" : "justify-between")}>
          {!collapsed && (
            <div className="flex items-center gap-2 min-w-0">
              <Avatar className="h-7 w-7">
                <AvatarFallback className="bg-sidebar-accent text-xs text-sidebar-foreground">
                  {user?.full_name?.charAt(0)?.toUpperCase() ?? "U"}
                </AvatarFallback>
              </Avatar>
              <span className="truncate text-xs text-sidebar-foreground/70">
                {user?.full_name ?? "User"}
              </span>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-7 w-7 text-sidebar-foreground/50 hover:text-sidebar-foreground"
          >
            {collapsed ? (
              <ChevronsRight className="h-4 w-4" />
            ) : (
              <ChevronsLeft className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <TooltipProvider delayDuration={0}>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Desktop sidebar */}
        <aside
          className={cn(
            "hidden border-r border-sidebar-border transition-[width] duration-200 md:block",
            collapsed ? "w-[52px]" : "w-[220px]",
          )}
        >
          <SidebarContent
            collapsed={collapsed}
            onToggle={() => setCollapsed((p) => !p)}
          />
        </aside>

        {/* Mobile sidebar */}
        <Sheet>
          <div className="flex flex-1 flex-col overflow-hidden">
            {/* Top bar */}
            <header className="flex h-14 items-center gap-3 border-b border-border bg-background px-4">
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden h-8 w-8">
                  <Menu className="h-4 w-4" />
                </Button>
              </SheetTrigger>

              <div className="flex-1" />

              <Button
                variant="outline"
                size="sm"
                className="hidden gap-2 text-xs text-muted-foreground sm:flex"
                onClick={() =>
                  document.dispatchEvent(
                    new KeyboardEvent("keydown", { key: "k", metaKey: true }),
                  )
                }
              >
                <Search className="h-3.5 w-3.5" />
                <span>Search...</span>
                <kbd className="pointer-events-none rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium">
                  ⌘K
                </kbd>
              </Button>
            </header>

            {/* Page content */}
            <main className="flex-1 overflow-auto">
              <div className="mx-auto max-w-7xl p-4 md:p-6">
                <Outlet />
              </div>
            </main>
          </div>

          <SheetContent side="left" className="w-[220px] p-0">
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <SidebarContent collapsed={false} onToggle={() => {}} />
          </SheetContent>
        </Sheet>

        {/* Global command palette */}
        <CommandPalette />
      </div>
    </TooltipProvider>
  )
}
