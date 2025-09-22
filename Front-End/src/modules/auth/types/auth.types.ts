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
  role: string
  is_active: boolean
  name?: string
  administrator_code?: string
  pathologist_code?: string
  resident_code?: string
  auxiliary_code?: string
  billing_code?: string
  last_access?: string
}

export interface TokenPayload {
  user_id: string
  email: string
  role: string
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

export type RoleEnum = 'administrator' | 'pathologist' | 'resident' | 'receptionist' | 'auxiliary' | 'billing'