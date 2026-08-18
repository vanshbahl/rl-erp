import { useState, type ComponentType } from "react"
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom"
import { CommandPalette } from "@/components/common/CommandPalette"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/stores/auth.store"
import {
  Boxes, ChevronsLeft, ChevronsRight, ClipboardList, CreditCard, Factory,
  LayoutDashboard, LogOut, Menu, Network, Package, Receipt, Search, Settings,
  ShoppingCart, Truck, UserRoundCog, Users,
} from "lucide-react"

interface NavItem {
  label: string
  icon: ComponentType<{ className?: string }>
  path?: string
}

interface NavSection {
  label: string
  items: NavItem[]
}

const NAV_SECTIONS: NavSection[] = [
  { label: "Overview", items: [{ label: "Dashboard", icon: LayoutDashboard, path: "/app/dashboard" }] },
  {
    label: "Sales",
    items: [
      { label: "Customers", icon: Users },
      { label: "Sales Orders", icon: ShoppingCart },
      { label: "Invoices", icon: Receipt },
      { label: "Payments", icon: CreditCard },
    ],
  },
  {
    label: "Inventory",
    items: [
      { label: "Products", icon: Package },
      { label: "Inventory", icon: Boxes },
    ],
  },
  {
    label: "Procurement",
    items: [
      { label: "Suppliers", icon: Truck },
      { label: "Purchase Orders", icon: ClipboardList },
    ],
  },
  {
    label: "Manufacturing",
    items: [
      { label: "BOMs", icon: Network },
      { label: "Production", icon: Factory },
    ],
  },
  {
    label: "Administration",
    items: [
      { label: "Users", icon: UserRoundCog },
      { label: "Settings", icon: Settings },
    ],
  },
]

function SidebarContent({
  collapsed,
  onToggle,
  onNavigate,
  collapsible = true,
}: {
  collapsed: boolean
  onToggle: () => void
  onNavigate?: () => void
  collapsible?: boolean
}) {
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()
  const location = useLocation()

  const renderNavItem = (item: NavItem) => {
    const isActive = item.path === location.pathname
    const content = (
      <>
        <item.icon className="h-4 w-4 shrink-0" />
        {!collapsed && <span className="truncate">{item.label}</span>}
      </>
    )
    const itemClassName = cn(
      "flex h-8 items-center gap-3 border-l-2 px-3 text-[13px] font-medium transition-colors",
      collapsed && "justify-center px-2",
      item.path
        ? isActive
          ? "border-sidebar-primary bg-sidebar-accent text-sidebar-primary"
          : "border-transparent text-sidebar-foreground/75 hover:bg-sidebar-accent hover:text-sidebar-foreground"
        : "cursor-not-allowed border-transparent text-sidebar-foreground/35",
    )
    const itemElement = item.path ? (
      <NavLink to={item.path} onClick={onNavigate} className={itemClassName}>
        {content}
      </NavLink>
    ) : (
      <div className={itemClassName} aria-disabled="true" title={collapsed ? undefined : "Available in a future phase"}>
        {content}
      </div>
    )

    if (!collapsed) return <div key={item.label}>{itemElement}</div>
    return (
      <Tooltip key={item.label}>
        <TooltipTrigger asChild>{itemElement}</TooltipTrigger>
        <TooltipContent side="right" className="text-xs">
          {item.label}{!item.path && " — future phase"}
        </TooltipContent>
      </Tooltip>
    )
  }

  return (
    <div className="flex h-full flex-col bg-sidebar">
      <div className={cn("flex h-14 shrink-0 items-center border-b border-sidebar-border px-4", collapsed && "justify-center px-2")}>
        {collapsed ? (
          <span className="text-base font-bold text-sidebar-primary">R</span>
        ) : (
          <div className="min-w-0">
            <p className="text-base font-bold leading-5 tracking-tight text-sidebar-foreground">RL-ERP</p>
            <p className="truncate text-[11px] leading-4 text-sidebar-foreground/55">Raman Laaminators</p>
          </div>
        )}
      </div>

      <ScrollArea className="flex-1">
        <nav className="space-y-4 px-2 py-3">
          {NAV_SECTIONS.map((section) => (
            <div key={section.label}>
              {!collapsed && (
                <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-[0.12em] text-sidebar-foreground/45">
                  {section.label}
                </p>
              )}
              <div className="space-y-0.5">{section.items.map(renderNavItem)}</div>
            </div>
          ))}
        </nav>
      </ScrollArea>

      <div className="shrink-0 border-t border-sidebar-border p-3">
        <div className={cn("flex items-center gap-2", collapsed && "justify-center")}>
          <Avatar className="h-8 w-8 border border-sidebar-border">
            <AvatarFallback className="bg-sidebar-accent text-xs font-semibold text-sidebar-foreground">
              {user?.username?.charAt(0)?.toUpperCase() ?? "U"}
            </AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-medium text-sidebar-foreground">{user?.username ?? "User"}</p>
              <p className="truncate text-[11px] uppercase tracking-wide text-sidebar-foreground/50">{user?.role ?? ""}</p>
            </div>
          )}
          {collapsible && (
            <Button variant="ghost" size="icon" onClick={onToggle} className="h-7 w-7 text-sidebar-foreground/50 hover:text-sidebar-foreground" aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
              {collapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
            </Button>
          )}
        </div>
        {!collapsed && (
          <>
            <Separator className="my-2 bg-sidebar-border" />
            <Button
              className="h-8 w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground"
              variant="ghost"
              size="sm"
              onClick={() => {
                logout()
                navigate("/login", { replace: true })
              }}
            >
              <LogOut className="h-4 w-4" />
              Log out
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const user = useAuthStore((state) => state.user)

  return (
    <TooltipProvider delayDuration={0}>
      <div className="flex h-screen overflow-hidden bg-background text-foreground">
        <aside className={cn("hidden shrink-0 border-r border-sidebar-border transition-[width] duration-200 md:block", collapsed ? "w-[52px]" : "w-[232px]")}>
          <SidebarContent collapsed={collapsed} onToggle={() => setCollapsed((previous) => !previous)} />
        </aside>

        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
            <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-card px-3 sm:px-4">
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 md:hidden" aria-label="Open navigation">
                  <Menu className="h-4 w-4" />
                </Button>
              </SheetTrigger>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold md:text-base">Dashboard</p>
                <p className="hidden text-[11px] text-muted-foreground sm:block">Operational overview</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="hidden w-56 justify-start gap-2 bg-background text-xs font-normal text-muted-foreground lg:flex"
                onClick={() => document.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))}
              >
                <Search className="h-3.5 w-3.5" />
                <span className="flex-1 text-left">Search pages and actions</span>
                <kbd className="border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium">⌘K</kbd>
              </Button>
              <div className="flex items-center gap-2 border-l border-border pl-3">
                <Avatar className="h-7 w-7 border border-border">
                  <AvatarFallback className="bg-muted text-[11px] font-semibold">{user?.username?.charAt(0)?.toUpperCase() ?? "U"}</AvatarFallback>
                </Avatar>
                <span className="hidden max-w-40 truncate text-xs text-muted-foreground sm:inline">
                  {user ? `${user.username} · ${user.role}` : "User"}
                </span>
              </div>
            </header>

            <main className="min-w-0 flex-1 overflow-auto">
              <div className="mx-auto max-w-[1440px] p-4 md:p-5 lg:p-6"><Outlet /></div>
            </main>
          </div>

          <SheetContent side="left" className="w-[min(86vw,280px)] p-0">
            <SheetTitle className="sr-only">RL-ERP navigation</SheetTitle>
            <SidebarContent collapsed={false} collapsible={false} onToggle={() => undefined} onNavigate={() => setMobileOpen(false)} />
          </SheetContent>
        </Sheet>

        <CommandPalette />
      </div>
    </TooltipProvider>
  )
}
