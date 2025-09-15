import { reactive } from 'vue'
import type { NotificationState } from '../types'

export function useNotifications() {
  const notification = reactive<NotificationState>({
    visible: false, type: 'success', title: '', message: ''
  })

  const showNotification = (
    type: NotificationState['type'], title: string, message: string, duration = 5000
  ): void => {
    Object.assign(notification, { type, title, message, visible: true })
    
    if (duration > 0) {
      setTimeout(() => closeNotification(), duration)
    }
  }

  const showSuccess = (title: string, message: string, duration = 0): void => {
    showNotification('success', title, message, duration)
  }

  const showError = (title: string, message: string, duration = 0): void => {
    showNotification('error', title, message, duration)
  }


  const closeNotification = (): void => {
    notification.visible = false
  }

  return {
    notification, showNotification, showSuccess, showError, closeNotification
  }
}
