/**
 * Tipos para el módulo de autenticación
 */

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface User {
  id: string
  email: string
  rol: string
  activo: boolean
  nombre?: string
  ultimo_acceso?: string
}

export interface TokenPayload {
  user_id: string
  email: string
  rol: string
  exp: number
  iat: number
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface LoginFormData {
  email: string
  password: string
  rememberMe: boolean
}

export interface AuthError {
  message: string
  code?: string
}

export type RolEnum = 'admin' | 'patologo' | 'residente' | 'recepcionista' | 'auxiliar' | 'facturacion'