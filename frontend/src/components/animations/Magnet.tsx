import React, { useRef, useState } from "react"
import { motion, useReducedMotion } from "motion/react"

interface MagnetProps {
  children: React.ReactNode
  padding?: number
  disabled?: boolean
}

export function Magnet({ children, padding = 100, disabled = false }: MagnetProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const prefersReducedMotion = useReducedMotion()

  const handleMouseMove = (e: React.MouseEvent) => {
    if (disabled || prefersReducedMotion) return
    if (!ref.current) return
    const { left, top, width, height } = ref.current.getBoundingClientRect()
    const centerX = left + width / 2
    const centerY = top + height / 2
    
    const distX = e.clientX - centerX
    const distY = e.clientY - centerY

    // Apply attraction only within padding radius
    if (Math.abs(distX) < padding && Math.abs(distY) < padding) {
      // Pull towards cursor very slightly for a solid premium feel
      setPosition({ x: distX * 0.02, y: distY * 0.02 })
    } else {
      setPosition({ x: 0, y: 0 })
    }
  }

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 })
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 300, damping: 30, mass: 0.1 }}
      className="inline-block"
    >
      {children}
    </motion.div>
  )
}
