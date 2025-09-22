// Resident API service: handles CRUD operations for residents
import apiClient from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface ResidentResponse {
  id: string
  resident_code: string
  resident_name: string
  initials?: string
  resident_email: string
  medical_license: string
  is_active: boolean
  observations?: string
  created_at: string
  updated_at: string
}

export interface ResidentUpdate {
  resident_name?: string
  initials?: string
  resident_email?: string
  medical_license?: string
  is_active?: boolean
  observations?: string
}

class ResidentApiService {
  private static readonly BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}/residents`
  private static readonly logPrefix = '[ResidentApiService]'

  // Get resident by code
  static async getByCode(code: string): Promise<ResidentResponse | null> {
    try {
      const response = await apiClient.get<ResidentResponse>(`${this.BASE_URL}/${code}`)
      return (response as any).data ?? response
    } catch (error) {
      console.error(`${this.logPrefix} Error getting resident by code:`, error)
      return null
    }
  }

  // Search resident by email
  static async getByEmail(email: string): Promise<ResidentResponse | null> {
    try {
      const response = await apiClient.get<ResidentResponse[]>(`${this.BASE_URL}/search`, {
        params: { q: email, limit: 1 }
      })
      const residents = (response as any).data ?? response
      return Array.isArray(residents) && residents.length > 0 ? residents[0] : null
    } catch (error) {
      console.error(`${this.logPrefix} Error searching resident by email:`, error)
      return null
    }
  }

  // Update resident
  static async update(code: string, data: ResidentUpdate): Promise<ResidentResponse | null> {
    try {
      const response = await apiClient.put<ResidentResponse>(`${this.BASE_URL}/${code}`, data)
      return (response as any).data ?? response
    } catch (error) {
      console.error(`${this.logPrefix} Error updating resident:`, error)
      return null
    }
  }
}

export { ResidentApiService }
