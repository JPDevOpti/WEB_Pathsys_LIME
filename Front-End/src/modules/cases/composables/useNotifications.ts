import { reactive } from 'vue'
import type { NotificationState } from '../types'

export function useNotifications() {
  // ============================================================================
  // ESTADO
  // ============================================================================
  
  const notification = reactive<NotificationState>({
    visible: false,
    type: 'success',
    title: '',
    message: ''
  })

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Muestra una notificación con los parámetros especificados
   * @param type - Tipo de notificación (success, error, warning, info)
   * @param title - Título de la notificación
   * @param message - Mensaje de la notificación
   * @param duration - Duración en milisegundos (0 = sin auto-cierre)
   */
  const showNotification = (
    type: NotificationState['type'],
    title: string,
    message: string,
    duration = 5000
  ): void => {
    notification.type = type
    notification.title = title
    notification.message = message
    notification.visible = true

    // Auto cerrar después del tiempo especificado
    if (duration > 0) {
      setTimeout(() => {
        closeNotification()
      }, duration)
    }
  }

  /**
   * Muestra una notificación de éxito
   * @param title - Título de la notificación
   * @param message - Mensaje de la notificación
   * @param duration - Duración en milisegundos (0 por defecto para que no se cierre automáticamente)
   */
  const showSuccess = (title: string, message: string, duration = 0): void => {
    showNotification('success', title, message, duration)
  }

  /**
   * Muestra una notificación de error
   * @param title - Título de la notificación
   * @param message - Mensaje de la notificación
   * @param duration - Duración en milisegundos (0 por defecto para errores)
   */
  const showError = (title: string, message: string, duration = 0): void => {
    showNotification('error', title, message, duration)
  }

  /**
   * Muestra una notificación de advertencia
   * @param title - Título de la notificación
   * @param message - Mensaje de la notificación
   * @param duration - Duración en milisegundos (0 por defecto para que no se cierre automáticamente)
   */
  const showWarning = (title: string, message: string, duration = 0): void => {
    showNotification('warning', title, message, duration)
  }

  /**
   * Muestra una notificación informativa
   * @param title - Título de la notificación
   * @param message - Mensaje de la notificación
   * @param duration - Duración en milisegundos (0 por defecto para que no se cierre automáticamente)
   */
  const showInfo = (title: string, message: string, duration = 0): void => {
    showNotification('info', title, message, duration)
  }

  /**
   * Cierra la notificación actual
   */
  const closeNotification = (): void => {
    notification.visible = false
  }

  // ============================================================================
  // RETORNO
  // ============================================================================

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
