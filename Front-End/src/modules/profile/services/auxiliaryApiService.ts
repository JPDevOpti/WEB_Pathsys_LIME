// Minimal API client wrapper for auxiliary endpoints
import apiClient from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface AuxiliarResponse {
  id: string
  auxiliar_code: string
  auxiliar_name: string
  auxiliar_email: string
  is_active: boolean
  observations?: string
  created_at: string
  updated_at: string
}

export interface AuxiliarUpdate {
  auxiliar_name?: string
  auxiliar_email?: string
  is_active?: boolean
  observations?: string
}

class AuxiliarApiService {
  private static readonly BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}/auxiliaries`
  
  // Internal GET helper with consistent error handling
  private static async getJson<T>(url: string, params?: Record<string, any>): Promise<T | null> {
    try {
      return await apiClient.get<T>(url, { params })
    } catch {
      return null
    }
  }

  // Internal PUT helper with consistent error handling
  private static async putJson<T>(url: string, data: unknown): Promise<T | null> {
    try {
      return await apiClient.put<T>(url, data)
    } catch {
      return null
    }
  }

  // Fetch auxiliary by unique code
  static async getByCode(code: string): Promise<AuxiliarResponse | null> {
    return this.getJson<AuxiliarResponse>(`${this.BASE_URL}/${code}`)
  }

  // Find first auxiliary by email (API returns an array)
  static async getByEmail(email: string): Promise<AuxiliarResponse | null> {
    const result = await this.getJson<AuxiliarResponse[] | { results?: AuxiliarResponse[] }>(
      `${this.BASE_URL}/search`,
      { q: email, limit: 1 }
    )
    if (!result) return null
    const list = Array.isArray(result) ? result : (result.results ?? [])
    return list.length ? list[0] : null
  }

  // Update basic auxiliary fields by code
  static async update(code: string, data: AuxiliarUpdate): Promise<AuxiliarResponse | null> {
    return this.putJson<AuxiliarResponse>(`${this.BASE_URL}/${code}`, data)
  }
}

export { AuxiliarApiService }
