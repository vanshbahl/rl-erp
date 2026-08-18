import { Navigate, Outlet } from "react-router-dom"
import { useAuthStore } from "@/stores/auth.store"

function AuthLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  )
}

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isAuthResolved = useAuthStore((state) => state.isAuthResolved)

  if (!isAuthResolved) {
    return <AuthLoading />
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}

export function PublicOnlyRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isAuthResolved = useAuthStore((state) => state.isAuthResolved)

  if (!isAuthResolved) {
    return <AuthLoading />
  }

  return isAuthenticated ? <Navigate to="/app/dashboard" replace /> : <Outlet />
}
