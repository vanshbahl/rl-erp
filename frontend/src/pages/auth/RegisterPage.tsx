import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function RegisterPage() {
  return (
    <div className="light flex min-h-screen items-center justify-center bg-[#f7f7f5] px-4 py-10 text-[#171717]">
      <Card className="w-full max-w-[420px] rounded-none border-neutral-300 bg-white shadow-none">
        <CardHeader className="space-y-6 p-6 sm:p-8">
          <div>
            <p className="text-lg font-semibold tracking-tight">RL-ERP</p>
            <p className="mt-1 text-sm text-neutral-500">Raman Laaminators</p>
          </div>
          <div className="space-y-2">
            <CardTitle className="text-2xl text-neutral-950">Need access to RL-ERP?</CardTitle>
            <CardDescription className="leading-6 text-neutral-600">
              User accounts are managed by the administrator. Contact the administrator if you need access to the ERP.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="px-6 pb-6 sm:px-8 sm:pb-8">
          <Button className="w-full" asChild variant="outline">
            <Link to="/login">Back to sign in</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
