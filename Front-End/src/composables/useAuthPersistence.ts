/**
 * Composable para manejar la persistencia de autenticación
 */

import { ref, onMounted } from 'vue'
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
      // Inicializar autenticación sin await para no bloquear la app
      authStore.initializeAuth()
      
      // Marcar como inicializado inmediatamente
      isInitialized.value = true
      
      // Esperar un poco para que la inicialización termine
      setTimeout(() => {
        // Si está autenticado y está en login, redirigir al dashboard
        if (authStore.isAuthenticated && router.currentRoute.value.path === '/login') {
          router.replace('/dashboard')
        }
      }, 100)
    } catch (error) {
      console.error('Error al inicializar la aplicación:', error)
      isInitialized.value = true
    }
  }

  /**
   * Verificar autenticación periódicamente (cada 15 minutos)
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
            router.push('/login')
          }
        } catch (error) {
          console.error('Error en verificación periódica de token:', error)
          // No redirigir en caso de error de red
        }
      }
    }, 15 * 60 * 1000) // 15 minutos en lugar de 5

    // Retornar el ID del intervalo para poder limpiarlo si es necesario
    return interval
  }

  /**
   * Manejar logout automático en caso de error de autenticación
   */
  const handleAuthError = () => {
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
  })

  return {
    isInitialized,
    initializeApp,
    handleAuthError
  }
}
