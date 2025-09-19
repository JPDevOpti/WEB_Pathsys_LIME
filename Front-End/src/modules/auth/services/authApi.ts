import type { LoginRequest, LoginResponse, User } from '../types/auth.types'

const API_BASE_URL = 'http://localhost:8000/api/v1'

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
   * Iniciar sesión
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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
        administrator_code: backendUser.administrator_code
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
   * Obtener información del usuario actual
   */
  async getCurrentUser(token: string): Promise<User> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
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
        administrator_code: data.administrator_code
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
   * Verificar validez del token
   */
  async verifyToken(token: string): Promise<{ valid: boolean; user?: User }> {
    try {
      // No hay endpoint /auth/verify en el back nuevo; usamos /auth/me
      const response = await fetch(`${this.baseUrl}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
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
      // En caso de error de red o servidor, no invalidar el token automáticamente
      console.error('Error verificando token:', error)
      throw error // Propagar el error para que el store pueda manejarlo apropiadamente
    }
  }

  /**
   * Renovar token
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string; expires_in: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Error al renovar token')
      }

      return await response.json()
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Error de conexión')
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(token: string): Promise<void> {
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