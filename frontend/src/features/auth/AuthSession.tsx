import { useEffect, type ReactNode } from "react"
import { authApi } from "@/features/auth/api"
import { useAuthStore } from "@/stores/auth.store"

interface AuthSessionProps {
  children: ReactNode
}

export function AuthSession({ children }: AuthSessionProps) {
  const token = useAuthStore((state) => state.token)

  useEffect(() => {
    let active = true
    const { logout, setAuthResolved, setUser } = useAuthStore.getState()

    if (!token) {
      setAuthResolved(true)
      return () => {
        active = false
      }
    }

    void authApi
      .getCurrentUser()
      .then((user) => {
        if (active) {
          setUser(user)
        }
      })
      .catch(() => {
        if (active) {
          logout()
        }
      })
      .finally(() => {
        if (active) {
          setAuthResolved(true)
        }
      })

    return () => {
      active = false
    }
  }, [token])

  return children
}
