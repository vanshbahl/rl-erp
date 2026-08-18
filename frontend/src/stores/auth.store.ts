import { create } from "zustand"
import { persist } from "zustand/middleware"

export interface User {
  id: number
  username: string
  email: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isAuthResolved: boolean
  login: (user: User, token: string) => void
  logout: () => void
  setUser: (user: User) => void
  setAuthResolved: (isAuthResolved: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isAuthResolved: false,

      login: (user, token) =>
        set({ user, token, isAuthenticated: true, isAuthResolved: true }),

      logout: () =>
        set({ user: null, token: null, isAuthenticated: false, isAuthResolved: true }),

      setUser: (user) => set({ user, isAuthenticated: true }),

      setAuthResolved: (isAuthResolved) => set({ isAuthResolved }),
    }),
    {
      name: "rl-erp-auth",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)
