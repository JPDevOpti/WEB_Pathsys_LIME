/**
 * Servicio de autenticación
 */

import type { LoginRequest, LoginResponse, User } from '../types/auth.types'

const API_BASE_URL = 'http://localhost:8000/api/v1'

class AuthService {
  /**
   * Realizar login
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error en el login')
    }

    return response.json()
  }

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Error al obtener información del usuario')
    }

    return response.json()
  }

  /**
   * Renovar token
   */
  async refreshToken(token: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Error al renovar token')
    }

    return response.json()
  }

  /**
   * Cerrar sesión
   */
  async logout(token: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Error al cerrar sesión')
    }
  }

  /**
   * Verificar si el token es válido
   */
  async verifyToken(token: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      return response.ok
    } catch {
      return false
    }
  }
}

export const authService = new AuthService()