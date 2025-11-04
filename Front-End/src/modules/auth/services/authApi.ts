import type { LoginRequest, LoginResponse, User } from '../types/auth.types'
import { API_CONFIG, getAuthHeaders } from '@/core/config/api.config'

const API_BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}`

export class AuthApiService {
  private static instance: AuthApiService
  private baseUrl: string

  private constructor() {
    this.baseUrl = API_BASE_URL
  }

  public static getInstance(): AuthApiService {
    if (!AuthApiService.instance) {
      AuthApiService.instance = new AuthApiService()
    }
    return AuthApiService.instance
  }

  /**
   * Sign in
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: { ...API_CONFIG.DEFAULT_HEADERS },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al iniciar sesión')
      }

      const data = await response.json()
      const backendToken = data.token || {}
      const backendUser = data.user || {}
      const mappedUser: User = {
        id: backendUser.id,
        email: backendUser.email,
        role: backendUser.role,
        is_active: backendUser.is_active ?? true,
        name: backendUser.name,
        administrator_code: backendUser.administrator_code,
        pathologist_code: backendUser.pathologist_code,
        resident_code: backendUser.resident_code,
        auxiliary_code: backendUser.auxiliary_code,
        billing_code: backendUser.billing_code
      }
      return {
        access_token: backendToken.access_token,
        token_type: backendToken.token_type || 'bearer',
        expires_in: backendToken.expires_in || 0,
        user: mappedUser
      }
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Error de conexión')
    }
  }

  /**
   * Get current user info
   */
  async getCurrentUser(token: string): Promise<User> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/me`, {
        method: 'GET',
        headers: { ...getAuthHeaders(token) },
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al obtener información del usuario')
      }

      const data = await response.json()
      const mapped: User = {
        id: data.id,
        email: data.email,
        role: data.role,
        is_active: data.is_active ?? true,
        name: data.name,
        administrator_code: data.administrator_code,
        pathologist_code: data.pathologist_code,
        resident_code: data.resident_code,
        auxiliary_code: data.auxiliary_code,
        billing_code: data.billing_code
      }
      return mapped
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Error de conexión')
    }
  }

  /**
   * Verify token validity
   */
  async verifyToken(token: string): Promise<{ valid: boolean; user?: User }> {
    try {
      // No hay endpoint /auth/verify en el back nuevo; usamos /auth/me
      const response = await fetch(`${this.baseUrl}/auth/me`, {
        method: 'GET',
        headers: { ...getAuthHeaders(token) },
      })

      if (!response.ok) {
        // Si es 401 o 403, el token es definitivamente inválido
        if (response.status === 401 || response.status === 403) {
          return { valid: false }
        }
        // Para otros errores (500, timeout, etc), asumir que es un problema temporal
        throw new Error(`Error del servidor: ${response.status}`)
      }

      const data = await response.json()
      const user: User = {
        id: data.id,
        email: data.email,
        role: data.role,
        is_active: data.is_active ?? true,
        name: data.name,
        administrator_code: data.administrator_code
      }
      return { valid: true, user }
    } catch (error) {
      throw error
    }
  }


  /**
   * Sign out
   */
  async logout(): Promise<void> {
    try {
      // No hay endpoint de logout en el back nuevo; limpiar en cliente
      return
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Error de conexión')
    }
  }
}

export const authApiService = AuthApiService.getInstance()