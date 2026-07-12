import { useEffect, useRef } from "react"
import { cn } from "@/lib/utils"

export function Noise({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animationId: number
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    const drawNoise = () => {
      const w = canvas.width
      const h = canvas.height
      const imgData = ctx.createImageData(w, h)
      const data = imgData.data

      for (let i = 0; i < data.length; i += 4) {
        const val = Math.random() * 255
        data[i] = val
        data[i + 1] = val
        data[i + 2] = val
        data[i + 3] = 12 // Very subtle opacity (alpha 0-255)
      }
      ctx.putImageData(imgData, 0, 0)
    }

    const loop = () => {
      drawNoise()
      // Only redraw occasionally to save battery/CPU, noise doesn't need 60fps
      setTimeout(() => {
        animationId = requestAnimationFrame(loop)
      }, 150)
    }

    window.addEventListener("resize", resize)
    resize()
    loop()

    return () => {
      window.removeEventListener("resize", resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className={cn(
        "pointer-events-none fixed inset-0 z-50 h-full w-full opacity-40 mix-blend-overlay",
        className
      )}
    />
  )
}
