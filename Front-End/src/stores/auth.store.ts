/**
 * Store de autenticación usando Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApiService } from '@/modules/auth/services/authApi'
import type { LoginRequest, User, AuthError } from '@/modules/auth/types/auth.types'

export const useAuthStore = defineStore('auth', () => {
  // Estado
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => {
    return user.value?.role || null
  })
  const isAdministrator = computed(() => userRole.value === 'administrator')
  const isAuxiliary = computed(() => userRole.value === 'auxiliar')
  const isPathologist = computed(() => userRole.value === 'pathologist')
  const isResident = computed(() => userRole.value === 'resident')
  const isPatient = computed(() => userRole.value === 'patient')
  const isBilling = computed(() => userRole.value === 'billing')

  // Acciones
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApiService.login(credentials)
      
      // Guardar token y usuario
      token.value = response.access_token
      user.value = response.user

      // Guardar en localStorage siempre para persistencia de sesión
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('auth_user', JSON.stringify(response.user))
      

      
      // Debug del estado completo
      debugUserState()

      return true
    } catch (err) {
      const authError = err as AuthError
      error.value = authError.message || 'Error signing in'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      // No hay logout en backend nuevo; solo limpiar cliente
    } catch (err) {
      // Error al cerrar sesión
    } finally {
      // Limpiar estado local
      user.value = null
      token.value = null
      
      // Limpiar localStorage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      
      isLoading.value = false
    }
  }

  const getCurrentUser = async (): Promise<boolean> => {
    if (!token.value) return false

    try {
      const currentUser = await authApiService.getCurrentUser(token.value)
      // Solo actualizar el usuario si obtenemos información más completa
      if (currentUser && Object.keys(currentUser).length > Object.keys(user.value || {}).length) {
        user.value = currentUser
        // Actualizar también en localStorage
        localStorage.setItem('auth_user', JSON.stringify(currentUser))
      }
      return true
    } catch (err) {
      // Error al obtener usuario actual
      // Si hay error, NO limpiar estado automáticamente
      // Solo limpiar si es un error de autenticación específico
      if (err instanceof Error && (err.message.includes('401') || err.message.includes('403'))) {
        await logout()
      }
      return false
    }
  }

  const verifyToken = async (): Promise<boolean> => {
    if (!token.value) return false

    try {
      const result = await authApiService.verifyToken(token.value)
      if (result.valid) {
        // No sobrescribir si ya hay usuario con info
        if (!user.value) user.value = result.user || null
        return true
      } else {
        // Token inválido, limpiar estado sin llamar logout para evitar bucles
        user.value = null
        token.value = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        return false
      }
    } catch (err) {
      // Error al verificar token (posible error de red)
      // En caso de error de red, mantener la sesión activa
      // No limpiar el estado automáticamente para evitar logout constante
      // Solo retornar false si es un error 401/403
      if (err instanceof Error && err.message.includes('401')) {
        user.value = null
        token.value = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        return false
      }
      return true // Mantener sesión en caso de error de red
    }
  }

  const initializeAuth = async (): Promise<void> => {
    // Si ya está autenticado, no hacer nada
    if (isAuthenticated.value) {
      return
    }

    // Intentar cargar desde localStorage
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')

    if (savedToken && savedUser) {
      try {
        // Establecer los valores para que isAuthenticated sea true
        token.value = savedToken
        user.value = JSON.parse(savedUser)
        
        // Debug del estado completo
        console.log('AuthStore - Initialized user:', user.value)
        console.log('AuthStore - User role:', user.value?.role)
        debugUserState()

        // NO ejecutar verificación inmediatamente para preservar los datos del usuario
        // La verificación se hará en el timer periódico si es necesario
      } catch (err) {
        // Error al parsear datos guardados
        // Solo limpiar si hay error de parsing
        await logout()
      }
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  // Función de debug para verificar el estado del usuario
  const debugUserState = () => {
    // Debug del estado del usuario (sin logs)
  }

  return {
    // Estado
    user,
    token,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    userRole,
    isAdministrator,
    isAuxiliary,
    isPathologist,
    isResident,
    isPatient,
    isBilling,
    
    // Acciones
    login,
    logout,
    getCurrentUser,
    verifyToken,
    initializeAuth,
    clearError,
    debugUserState
  }
})