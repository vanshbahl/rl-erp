import { lazy } from "react"
import { createBrowserRouter, Navigate } from "react-router-dom"

const PublicLayout = lazy(() => import("@/pages/public/PublicLayout"))
const LandingPage = lazy(() => import("@/pages/public/LandingPage"))

const AppShell = lazy(() => import("@/pages/app/AppShell"))
const DashboardPage = lazy(() => import("@/pages/app/DashboardPage"))

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { index: true, element: <LandingPage /> },
    ],
  },
  {
    path: "/app",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
    ],
  },
])
