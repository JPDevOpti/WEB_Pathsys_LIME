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
      
      // Si hay sesión cargada, verificar inmediatamente que el token sea válido y refrescarlo si es necesario
      if (authStore.isAuthenticated && authStore.token) {
        console.log('🔍 [AUTH PERSISTENCE] Checking token during app initialization...')
        
        // First try to refresh if near expiration
        const refreshed = await authStore.checkAndRefreshToken()
        
        if (!refreshed) {
          // If refresh failed, verify the token
          const isValid = await authStore.verifyToken()
          if (!isValid) {
            console.warn('⚠️ [AUTH PERSISTENCE] Token invalid during initialization, logging out')
            // Logout y redireccionar a login
            await authStore.logout()
            if (router.currentRoute.value.path !== '/login') {
              router.replace('/login')
            }
          }
        } else {
          console.log('✅ [AUTH PERSISTENCE] Token verified/refreshed during initialization')
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
   * Iniciar timer para verificación y refresh automático del token
   */
  const startTokenRefreshTimer = () => {
    const interval = setInterval(async () => {
      if (authStore.isAuthenticated && authStore.token) {
        try {
          // First try to refresh the token if it's near expiration
          const refreshed = await authStore.checkAndRefreshToken()
          
          if (refreshed) {
            console.log('🔄 [AUTH PERSISTENCE] Token checked/refreshed successfully')
          } else {
            // If refresh failed, verify the token
            const isValid = await authStore.verifyToken()
            if (!isValid) {
              console.warn('Token inválido detectado en verificación periódica')
              // Logout para limpiar estado
              await authStore.logout()
              router.push('/login')
            }
          }
        } catch (error) {
          console.error('Error en verificación/refresh periódico de token:', error)
          // No redirigir en caso de error de red
        }
      }
    }, 2 * 60 * 1000) // 2 minutos (check more frequently for refresh)

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
    // Start the timer sooner to prevent timing issues
    setTimeout(() => {
      startTokenRefreshTimer()
    }, 10000) // Esperar 10 segundos antes de iniciar verificaciones periódicas

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
