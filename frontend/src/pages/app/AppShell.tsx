import { useState, type ComponentType } from "react"
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom"
import { CommandPalette } from "@/components/common/CommandPalette"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/stores/auth.store"
import {
  BarChart3,
  Boxes,
  ChevronDown,
  ChevronsLeft,
  ChevronsRight,
  ClipboardList,
  CreditCard,
  Factory,
  LayoutDashboard,
  LogOut,
  Menu,
  Network,
  Package,
  Receipt,
  Search,
  Settings,
  ShoppingCart,
  Truck,
  UserRoundCog,
  Users,
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
  { label: "Reporting", items: [{ label: "Reports", icon: BarChart3 }] },
  {
    label: "Administration",
    items: [
      { label: "Users", icon: UserRoundCog },
      { label: "Settings", icon: Settings },
    ],
  },
]

function openCommandPalette() {
  document.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))
}

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

  const handleLogout = () => {
    logout()
    navigate("/login", { replace: true })
  }

  const renderNavItem = (item: NavItem) => {
    const isActive = item.path === location.pathname
    const content = (
      <>
        <item.icon className="h-4 w-4 shrink-0" />
        {!collapsed && <span className="truncate">{item.label}</span>}
      </>
    )
    const itemClassName = cn(
      "flex h-9 items-center gap-3 rounded-md border-l-2 px-3 text-[13px] font-medium transition-colors",
      collapsed && "justify-center rounded-md border-l-0 px-2",
      item.path
        ? isActive
          ? "border-sidebar-primary/35 bg-sidebar-accent/75 text-sidebar-primary"
          : "border-transparent text-sidebar-foreground/70 hover:bg-sidebar-accent/45 hover:text-sidebar-foreground/90"
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
      <div className={cn("flex h-16 shrink-0 items-center border-b border-sidebar-border px-4", collapsed && "justify-center px-2")}>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
          RL
        </div>
        {!collapsed && (
          <div className="ml-3 min-w-0">
            <p className="truncate text-[13px] font-semibold leading-4 text-sidebar-foreground">Raman Laaminators</p>
            <p className="text-[11px] leading-4 text-sidebar-foreground/55">RL-ERP</p>
          </div>
        )}
      </div>

      <ScrollArea className="flex-1">
        <nav className="space-y-3 px-2 py-3">
          {NAV_SECTIONS.map((section) => (
            <div key={section.label}>
              {!collapsed && (
                <p className="mb-1 px-3 text-[10px] font-medium uppercase tracking-[0.1em] text-sidebar-foreground/40">
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
            <AvatarFallback className="bg-card text-xs font-semibold text-sidebar-foreground">
              {user?.username?.charAt(0)?.toUpperCase() ?? "U"}
            </AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-medium text-sidebar-foreground">{user?.username ?? "User"}</p>
              <p className="truncate text-[10px] uppercase tracking-[0.08em] text-sidebar-foreground/50">{user?.role ?? ""}</p>
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
            <Button className="h-8 w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground" variant="ghost" size="sm" onClick={handleLogout}>
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
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()
  const dateLabel = new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date())

  const handleLogout = () => {
    logout()
    navigate("/login", { replace: true })
  }

  return (
    <TooltipProvider delayDuration={0}>
      <div className="flex h-screen overflow-hidden bg-background text-foreground">
        <aside className={cn("hidden shrink-0 border-r border-sidebar-border/70 transition-[width] duration-200 md:block", collapsed ? "w-[56px]" : "w-[224px]")}>
          <SidebarContent collapsed={collapsed} onToggle={() => setCollapsed((previous) => !previous)} />
        </aside>

        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
            <header className="flex h-16 shrink-0 items-center gap-3 border-b border-border-subtle bg-card px-3 sm:px-5">
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9 md:hidden" aria-label="Open navigation">
                  <Menu className="h-[18px] w-[18px]" />
                </Button>
              </SheetTrigger>
              <span className="text-sm font-semibold md:hidden">RL-ERP</span>

              <Button
                variant="outline"
                className="hidden h-10 max-w-[620px] flex-1 justify-start gap-3 rounded-lg border-border-subtle bg-secondary/65 px-4 text-[13px] font-normal text-muted-foreground shadow-none md:flex"
                onClick={openCommandPalette}
              >
                <Search className="h-4 w-4" />
                <span className="flex-1 text-left">Search products, customers, orders...</span>
                <kbd className="border-l border-border-subtle pl-3 text-[10px] font-normal text-muted-foreground/70">⌘K</kbd>
              </Button>

              <div className="ml-auto flex items-center gap-2">
                <Button variant="ghost" size="icon" className="h-9 w-9 md:hidden" onClick={openCommandPalette} aria-label="Open search">
                  <Search className="h-[18px] w-[18px]" />
                </Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="flex items-center gap-2 rounded-md p-1.5 text-left transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/30" aria-label="Open user menu">
                      <Avatar className="h-8 w-8 border border-border">
                        <AvatarFallback className="bg-foreground text-[11px] font-semibold text-background">
                          {user?.username?.charAt(0)?.toUpperCase() ?? "U"}
                        </AvatarFallback>
                      </Avatar>
                      <span className="hidden min-w-0 sm:block">
                        <span className="block max-w-32 truncate text-xs font-medium">{user?.username ?? "User"}</span>
                        <span className="block text-[10px] uppercase tracking-wide text-muted-foreground">{user?.role ?? ""}</span>
                      </span>
                      <ChevronDown className="hidden h-3.5 w-3.5 text-muted-foreground sm:block" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuLabel>
                      <span className="block text-xs font-medium">{user?.username ?? "User"}</span>
                      <span className="block text-[10px] font-normal uppercase tracking-wide text-muted-foreground">{user?.role ?? ""}</span>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onSelect={handleLogout}>
                      <LogOut className="h-4 w-4" />
                      Log out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </header>

            <div className="flex h-12 shrink-0 items-center border-b border-border-subtle bg-card px-4 sm:px-6">
              <div className="flex min-w-0 items-center gap-2">
                <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
                <span className="truncate text-sm font-medium">Dashboard</span>
              </div>
              <span className="ml-auto text-xs text-muted-foreground">Today · {dateLabel}</span>
            </div>

            <main className="min-w-0 flex-1 overflow-auto">
              <div className="mx-auto max-w-[1440px] p-4 sm:p-5 lg:p-6"><Outlet /></div>
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
