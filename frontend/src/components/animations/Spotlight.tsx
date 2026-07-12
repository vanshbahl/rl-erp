import { cn } from "@/lib/utils"

export function Spotlight({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "pointer-events-none fixed inset-0 z-10 flex items-start justify-center overflow-hidden mix-blend-screen opacity-30 dark:opacity-20 transition-opacity duration-700",
        className
      )}
    >
      <div
        className="w-[800px] h-[500px] -mt-20 rounded-[100%] bg-primary/20 blur-[150px]"
      />
    </div>
  )
}
