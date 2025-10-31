/**
 * Store de autenticación usando Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApiService } from '@/modules/auth/services/authApi'
import { TokenRefreshService } from '@/services/tokenRefreshService'
import type { LoginRequest, User, AuthError } from '@/modules/auth/types/auth.types'

export const useAuthStore = defineStore('auth', () => {
  // Estado
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => {
    const hasToken = !!token.value
    const hasUser = !!user.value
    const result = hasToken && hasUser
    
    return result
  })
  const userRole = computed(() => {
    return user.value?.role || null
  })
  // Normalizar rol para compatibilidad con variantes en español e inglés
  const normalizedRole = computed(() => (userRole.value || '').toString().trim().toLowerCase())
  const isAdministrator = computed(() => ['administrator', 'admin', 'administrador'].includes(normalizedRole.value))
  const isAuxiliary = computed(() => ['auxiliar', 'auxiliary', 'assistant'].includes(normalizedRole.value))
  const isPathologist = computed(() => ['pathologist', 'patologo', 'patólogo'].includes(normalizedRole.value))
  const isResident = computed(() => ['resident', 'residente'].includes(normalizedRole.value))
  const isPatient = computed(() => ['patient', 'paciente'].includes(normalizedRole.value))
  const isBilling = computed(() => ['billing', 'facturacion', 'facturación'].includes(normalizedRole.value))

  // Actions
  const login = async (credentials: LoginRequest, rememberMe: boolean = false): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApiService.login(credentials)
      
      // Save token and user
      token.value = response.access_token
      user.value = response.user

      // Persist session based on rememberMe: localStorage if true, sessionStorage if false
      const storage = rememberMe ? window.localStorage : window.sessionStorage
      storage.setItem('auth_token', response.access_token)
      storage.setItem('auth_user', JSON.stringify(response.user))
      // Save expiration timestamp by decoding JWT 'exp' claim if available
      try {
        const parts = response.access_token?.split('.') || []
        if (parts.length === 3) {
          const payloadJson = JSON.parse(atob(parts[1]))
          const expSec = Number(payloadJson?.exp)
          if (!Number.isNaN(expSec) && expSec > 0) {
            const expiresAt = expSec * 1000
            storage.setItem('auth_expires_at', String(expiresAt))
          } else if (response.expires_in && response.expires_in > 0) {
            const expiresAt = Date.now() + response.expires_in * 1000
            storage.setItem('auth_expires_at', String(expiresAt))
          }
        } else if (response.expires_in && response.expires_in > 0) {
          const expiresAt = Date.now() + response.expires_in * 1000
          storage.setItem('auth_expires_at', String(expiresAt))
        }
      } catch (_e) {
        // Fallback to expires_in on decode errors
        if (response.expires_in && response.expires_in > 0) {
          const expiresAt = Date.now() + response.expires_in * 1000
          storage.setItem('auth_expires_at', String(expiresAt))
        }
      }

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
      // No server-side logout; just clear client state
    } catch (err) {
      // Error while logging out
    } finally {
      // Clear local state
      user.value = null
      token.value = null
      
      // Clear both storages
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_expires_at')
      // Comentario: Limpiar claves relacionadas con firma para evitar falsos positivos en nueva sesión
      localStorage.removeItem('signature_url')
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('auth_user')
      sessionStorage.removeItem('auth_expires_at')
      sessionStorage.removeItem('signature_missing_notified')
      sessionStorage.removeItem('signature_url')
      
      isLoading.value = false
    }
  }

  const getCurrentUser = async (): Promise<boolean> => {
    if (!token.value) return false

    try {
      const currentUser = await authApiService.getCurrentUser(token.value)
      // Only update user if we get more complete information
      if (currentUser && Object.keys(currentUser).length > Object.keys(user.value || {}).length) {
        user.value = currentUser
        // Update also in persistent storage (prefer localStorage, fallback to sessionStorage)
        const storage = localStorage.getItem('auth_token') ? localStorage : sessionStorage
        storage.setItem('auth_user', JSON.stringify(currentUser))
      }
      return true
    } catch (err) {
      // Error getting current user
      // If there is an error, DO NOT clear state automatically
      // Only clear if it is a specific authentication error
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
        // Do not overwrite if there is already user info
        if (!user.value) user.value = result.user || null
        return true
      } else {
        // Invalid token, perform logout to clear state consistently
        await logout()
        return false
      }
    } catch (err) {
      // Error verifying token (possible network error)
      // In case of network error, keep the session active
      // Do not clear the state automatically to avoid constant logout
      // Only return false if it is a 401/403 error
      if (err instanceof Error && err.message.includes('401')) {
        user.value = null
        token.value = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        sessionStorage.removeItem('auth_token')
        sessionStorage.removeItem('auth_user')
        return false
      }
      return true // Keep session on network error
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    if (!token.value) {
      return false
    }

    try {
      const refreshResponse = await TokenRefreshService.refreshToken()
      
      // Calculate new expiration time
      const expiresAt = Date.now() + (refreshResponse.expires_in * 1000)
      
      // Update in persistent storage first (prefer localStorage, fallback to sessionStorage)
      const storage = localStorage.getItem('auth_token') ? localStorage : sessionStorage
      storage.setItem('auth_token', refreshResponse.access_token)
      storage.setItem('auth_expires_at', expiresAt.toString())
      
      // Then update the token in the store
      token.value = refreshResponse.access_token
      
      return true
    } catch (error: any) {
      console.error('❌ [TOKEN REFRESH] Failed to refresh token:', error)
      
      // If refresh fails due to authentication error, logout
      if (error?.response?.status === 401 || error?.response?.status === 403) {
        await logout()
      }
      
      return false
    }
  }

  const checkAndRefreshToken = async (): Promise<boolean> => {
    if (!token.value) return false

    try {
      // Check if token is near expiration (within 15 minutes)
      if (TokenRefreshService.isTokenNearExpiration(token.value)) {
        const refreshResult = await refreshToken()
        
        if (refreshResult) {
          // Verify the token was properly stored
          const storedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
          if (storedToken && storedToken === token.value) {
            return true
          } else {
            return false
          }
        }
        
        return refreshResult
      }
      
      return true
    } catch (error) {
      console.error('Error checking token expiration:', error)
      return false
    }
  }

  const initializeAuth = async (): Promise<void> => {
    // If already authenticated, do nothing
    if (isAuthenticated.value) {
      return
    }

    // Try loading from either localStorage or sessionStorage
    const savedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user') || sessionStorage.getItem('auth_user')

    if (savedToken && savedUser) {
      try {
        // If the token is expired, logout immediately
        const savedExpiresAt = localStorage.getItem('auth_expires_at') || sessionStorage.getItem('auth_expires_at')
        
        if (savedExpiresAt && Number(savedExpiresAt) > 0 && Date.now() > Number(savedExpiresAt)) {
          await logout()
          return
        }

        // Set values so isAuthenticated becomes true
        token.value = savedToken
        user.value = JSON.parse(savedUser)

        // DO NOT execute verification immediately to preserve user data
        // Verification will be done by a periodic timer if necessary
      } catch (err) {
        // Error parsing saved data
        // Only clear if there is parsing error
        await logout()
      }
    }
  }

  const clearError = (): void => {
    error.value = null
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
    refreshToken,
    checkAndRefreshToken,
    initializeAuth,
    clearError
  }
})