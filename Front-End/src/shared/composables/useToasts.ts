import { reactive } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'
export type ToastAction = 'create' | 'update' | 'delete' | 'generic'

export interface ToastItem {
  id: string
  type: ToastType
  action: ToastAction
  title: string
  message: string
  duration: number
}

const state = reactive({ toasts: [] as ToastItem[] })

function add(toast: Omit<ToastItem, 'id'>) {
  const id = `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  const item: ToastItem = { id, ...toast }
  state.toasts.push(item)
  if (item.duration > 0) setTimeout(() => remove(id), item.duration)
  return id
}

function remove(id: string) {
  const idx = state.toasts.findIndex(t => t.id === id)
  if (idx !== -1) state.toasts.splice(idx, 1)
}

function show(type: ToastType, action: ToastAction, title: string, message: string, duration = 4000) {
  return add({ type, action, title, message, duration })
}

export function useToasts() {
  return {
    toasts: state.toasts,
    show,
    remove,
    success: (action: ToastAction, title: string, message: string, duration?: number) => show('success', action, title, message, duration),
    error: (action: ToastAction, title: string, message: string, duration?: number) => show('error', action, title, message, duration),
    warning: (action: ToastAction, title: string, message: string, duration?: number) => show('warning', action, title, message, duration),
    info: (action: ToastAction, title: string, message: string, duration?: number) => show('info', action, title, message, duration)
  }
}


