'use client'

import React from 'react'

type ToastItem = {
  id: string
  message: string
  type?: 'success' | 'error'
}

// Global listeners and toast state
let listeners: ((items: ToastItem[]) => void)[] = []
let toasts: ToastItem[] = []

// Function to push a new toast
export function pushToast(
  message: string,
  type: 'success' | 'error' = 'success'
) {
  const id = String(Date.now())
  toasts = [{ id, message, type }, ...toasts].slice(0, 5) // Limit to 5 toasts
  listeners.forEach((listener) => listener(toasts))

  // Auto-remove toast after 4 seconds
  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id)
    listeners.forEach((listener) => listener(toasts))
  }, 4000)
}

// Toast component
export default function Toast() {
  const [items, setItems] = React.useState<ToastItem[]>([])

  React.useEffect(() => {
    const listener = (updatedToasts: ToastItem[]) => setItems(updatedToasts)
    listeners.push(listener)
    setItems(toasts)

    return () => {
      listeners = listeners.filter((l) => l !== listener)
    }
  }, [])

  return (
    <div className="fixed right-4 top-6 z-50 flex flex-col gap-2">
      {items.map((toast) => (
        <div
          key={toast.id}
          className={`max-w-xs p-3 rounded-lg shadow-md text-white transition-opacity duration-300 ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          }`}
        >
          {toast.message}
        </div>
      ))}
    </div>
  )
}
