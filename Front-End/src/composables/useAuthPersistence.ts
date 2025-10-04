/**
 * Composable para manejar la persistencia de autenticación
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useRouter } from 'vue-router'

export function useAuthPersistence() {
  const authStore = useAuthStore()
  const router = useRouter()
  const isInitialized = ref(false)

  /**
   * Inicializar autenticación al cargar la aplicación
   */
  const initializeApp = async () => {
    try {
      // Inicializar autenticación y verificar token antes de habilitar la app
      await authStore.initializeAuth()
      
      // Si hay sesión cargada, verificar inmediatamente que el token sea válido
      if (authStore.isAuthenticated && authStore.token) {
        const isValid = await authStore.verifyToken()
        if (!isValid) {
          // Logout y redireccionar a login
          await authStore.logout()
          if (router.currentRoute.value.path !== '/login') {
            router.replace('/login')
          }
        }
      }

      // Marcar como inicializado
      isInitialized.value = true

      // Si está autenticado y está en login, redirigir al dashboard
      if (authStore.isAuthenticated && router.currentRoute.value.path === '/login') {
        router.replace('/dashboard')
      }
    } catch (error) {
      console.error('Error al inicializar la aplicación:', error)
      isInitialized.value = true
    }
  }

  /**
   * Verificar autenticación periódicamente (cada 60 minutos)
   * Reducido la frecuencia para evitar interferir con la navegación
   */
  const startTokenRefreshTimer = () => {
    const interval = setInterval(async () => {
      // Solo verificar si hay un token y el usuario está realmente autenticado
      if (authStore.isAuthenticated && authStore.token) {
        try {
          const isValid = await authStore.verifyToken()
          if (!isValid && router.currentRoute.value.path !== '/login') {
            console.warn('Token expirado, redirigiendo a login')
            clearInterval(interval) // Limpiar el intervalo antes de redirigir
            // Logout para limpiar estado
            await authStore.logout()
            router.push('/login')
          }
        } catch (error) {
          console.error('Error en verificación periódica de token:', error)
          // No redirigir en caso de error de red
        }
      }
    }, 60 * 60 * 1000) // 60 minutos (1 hora)

    // Retornar el ID del intervalo para poder limpiarlo si es necesario
    return interval
  }

  /**
   * Manejar logout automático en caso de error de autenticación
   */
  const handleAuthError = async () => {
    await authStore.logout()
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  }

  // Listener para eventos globales de 401 desde Axios
  const onUnauthorized = async () => {
    console.warn('Evento global auth-unauthorized recibido: cerrando sesión')
    await authStore.logout()
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
  }

  onMounted(() => {
    initializeApp()
    // Retrasar el inicio del timer para dar tiempo a que la app se estabilice
    setTimeout(() => {
      startTokenRefreshTimer()
    }, 30000) // Esperar 30 segundos antes de iniciar verificaciones periódicas

    // Escuchar eventos de 401 no autorizado desde axios
    window.addEventListener('auth-unauthorized', onUnauthorized as EventListener)
  })

  onUnmounted(() => {
    window.removeEventListener('auth-unauthorized', onUnauthorized as EventListener)
  })

  return {
    isInitialized,
    initializeApp,
    handleAuthError
  }
}
