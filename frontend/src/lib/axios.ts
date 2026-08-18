import axios from "axios"
import { queryClient } from "@/lib/query"
import { useAuthStore } from "@/stores/auth.store"

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15_000,
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const stored = localStorage.getItem("rl-erp-auth")
  if (stored) {
    try {
      const parsed = JSON.parse(stored) as { state?: { token?: string } }
      const token = parsed?.state?.token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch {
      // malformed storage — ignore
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        useAuthStore.getState().logout()
        queryClient.clear()
        if (window.location.pathname !== "/login") {
          window.location.replace("/login")
        }
      }
    }
    return Promise.reject(error)
  },
)
