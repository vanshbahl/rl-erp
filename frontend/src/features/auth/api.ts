import axios from "axios"
import { api } from "@/lib/axios"
import type { User } from "@/stores/auth.store"

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterPayload extends LoginCredentials {
  username: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>("/auth/login", credentials)
    return data
  },

  async register(payload: RegisterPayload): Promise<void> {
    await api.post("/auth/register", payload)
  },

  async getCurrentUser(token?: string): Promise<User> {
    const { data } = await api.get<User>("/users/me", {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    })
    return data
  },
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) {
    return fallback
  }

  if (!error.response) {
    return "Unable to reach the server. Please try again."
  }

  const detail = error.response.data?.detail
  return typeof detail === "string" ? detail : fallback
}
