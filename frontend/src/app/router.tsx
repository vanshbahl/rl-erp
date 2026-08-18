/* eslint-disable react-refresh/only-export-components */
import { lazy } from "react"
import { createBrowserRouter, Navigate } from "react-router-dom"
import { ProtectedRoute, PublicOnlyRoute } from "@/features/auth/RouteGuards"

const PublicLayout = lazy(() => import("@/pages/public/PublicLayout"))
const LandingPage = lazy(() => import("@/pages/public/LandingPage"))

const AppShell = lazy(() => import("@/pages/app/AppShell"))
const DashboardPage = lazy(() => import("@/pages/app/DashboardPage"))
const CustomersPage = lazy(() => import("@/features/customers/pages/CustomersPage"))
const ProductsPage = lazy(() => import("@/features/products/pages/ProductsPage"))
const InventoryPage = lazy(() => import("@/features/inventory/pages/InventoryPage"))
const SuppliersPage = lazy(() => import("@/features/suppliers/pages/SuppliersPage"))
const SalesOrdersPage = lazy(() => import("@/features/orders/pages/SalesOrdersPage"))
const InvoicesPage = lazy(() => import("@/features/invoices/pages/InvoicesPage"))
const PaymentsPage = lazy(() => import("@/features/payments/pages/PaymentsPage"))
const LoginPage = lazy(() => import("@/pages/auth/LoginPage"))
const RegisterPage = lazy(() => import("@/pages/auth/RegisterPage"))

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { index: true, element: <LandingPage /> },
    ],
  },
  {
    element: <PublicOnlyRoute />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: "/app",
        element: <AppShell />,
        children: [
          { index: true, element: <Navigate to="dashboard" replace /> },
          { path: "dashboard", element: <DashboardPage /> },
          { path: "customers", element: <CustomersPage /> },
          { path: "products", element: <ProductsPage /> },
          { path: "inventory", element: <InventoryPage /> },
          { path: "suppliers", element: <SuppliersPage /> },
          { path: "sales", element: <SalesOrdersPage /> },
          { path: "invoices", element: <InvoicesPage /> },
          { path: "payments", element: <PaymentsPage /> },
        ],
      },
    ],
  },
])
