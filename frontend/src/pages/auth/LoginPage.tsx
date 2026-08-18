import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { Eye, EyeOff } from "lucide-react"
import { authApi, getApiErrorMessage } from "@/features/auth/api"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuthStore } from "@/stores/auth.store"

export default function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const devBypassEnabled =
    import.meta.env.DEV && import.meta.env.VITE_DEV_AUTH_BYPASS === "true"

  const completeLogin = async (accessToken: string) => {
    const user = await authApi.getCurrentUser(accessToken)
    login(user, accessToken)
    navigate("/app/dashboard", { replace: true })
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const { access_token } = await authApi.login({ email, password })
      await completeLogin(access_token)
      toast.success("Signed in successfully")
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to sign in. Please try again."))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDevLogin = async () => {
    setError(null)
    setIsSubmitting(true)

    try {
      const { access_token } = await authApi.devLogin()
      await completeLogin(access_token)
      toast.success("Development session started")
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Development login is unavailable."))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="light flex min-h-screen items-center justify-center bg-[#f5f5f3] px-4 py-10 text-[#202124]">
      <Card className="w-full max-w-[420px] rounded-lg border-neutral-200/90 bg-white shadow-none">
        <CardHeader className="space-y-6 p-6 sm:p-8">
          <div>
            <p className="text-xl font-bold tracking-tight text-neutral-950">RL-ERP</p>
            <p className="mt-1 text-sm text-neutral-500">Raman Laaminators</p>
          </div>
          <div className="space-y-2">
            <CardTitle className="text-2xl text-neutral-950">Welcome back</CardTitle>
            <CardDescription className="text-neutral-600">
              Sign in to access your ERP workspace.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="px-6 pb-6 sm:px-8 sm:pb-8">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label className="text-neutral-800" htmlFor="email">Email</Label>
              <Input
                className="border-neutral-200 bg-[#fafaf8] text-neutral-950"
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label className="text-neutral-800" htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  className="border-neutral-200 bg-[#fafaf8] pr-11 text-neutral-950"
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-neutral-500 hover:text-neutral-800"
                  onClick={() => setShowPassword((visible) => !visible)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button className="w-full" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>
          </form>
          <div className="mt-5 flex flex-col items-center gap-3 text-sm text-neutral-600">
            <button
              type="button"
              className="hover:text-neutral-950 hover:underline"
              onClick={() => toast.info("Password recovery is not configured yet. Contact the system administrator.")}
            >
              Forgot password?
            </button>
            <Link className="font-medium text-primary hover:underline" to="/register">
              Need access? Contact administrator
            </Link>
          </div>
          {devBypassEnabled && (
            <div className="mt-6 border-t border-neutral-200 pt-5">
              <Button
                className="w-full border-neutral-200 bg-[#fafaf8] text-neutral-700 shadow-none hover:bg-neutral-100 hover:text-neutral-950"
                type="button"
                variant="outline"
                disabled={isSubmitting}
                onClick={handleDevLogin}
              >
                Developer: Skip login
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
