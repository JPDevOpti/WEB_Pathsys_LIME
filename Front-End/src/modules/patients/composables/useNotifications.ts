import { ref } from 'vue'

export interface NotificationState {
  visible: boolean
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
}

export function useNotifications() {
  const notification = ref<NotificationState>({
    visible: false,
    type: 'info',
    title: '',
    message: ''
  })

  const showNotification = (
    type: NotificationState['type'],
    title: string,
    message: string = '',
    autoCloseDelay: number = 5000
  ) => {
    notification.value = {
      visible: true,
      type,
      title,
      message
    }

    if (autoCloseDelay > 0) {
      setTimeout(() => {
        closeNotification()
      }, autoCloseDelay)
    }
  }

  const showSuccess = (title: string, message: string = '', autoCloseDelay: number = 5000) => {
    showNotification('success', title, message, autoCloseDelay)
  }

  const showError = (title: string, message: string = '', autoCloseDelay: number = 0) => {
    showNotification('error', title, message, autoCloseDelay)
  }

  const showWarning = (title: string, message: string = '', autoCloseDelay: number = 5000) => {
    showNotification('warning', title, message, autoCloseDelay)
  }

  const showInfo = (title: string, message: string = '', autoCloseDelay: number = 5000) => {
    showNotification('info', title, message, autoCloseDelay)
  }

  const closeNotification = () => {
    notification.value.visible = false
  }

  return {
    notification,
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    closeNotification
  }
}

