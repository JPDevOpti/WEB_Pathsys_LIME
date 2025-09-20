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

  /**
   * Obtener residente por código
   */
  static async getByCode(code: string): Promise<ResidentResponse | null> {
    try {
      const resident = await apiClient.get<ResidentResponse>(`${this.BASE_URL}/${code}`)
      return resident
    } catch (error) {
      console.error('Error al obtener residente:', error)
      return null
    }
  }

  /**
   * Buscar residente por email
   */
  static async getByEmail(email: string): Promise<ResidentResponse | null> {
    try {
      console.log('🔍 ResidentApiService.getByEmail - Buscando residente para:', email)
      const residents = await apiClient.get<ResidentResponse[]>(`${this.BASE_URL}/search`, {
        params: { resident_email: email, limit: 1 }
      })
      
      console.log('📋 ResidentApiService.getByEmail - Respuesta completa:', residents)
      
      // El endpoint devuelve un array directamente
      if (Array.isArray(residents) && residents.length > 0) {
        console.log('✅ ResidentApiService.getByEmail - Residente encontrado:', residents[0])
        return residents[0] as ResidentResponse
      }
      
      console.log('❌ ResidentApiService.getByEmail - No se encontraron residentes')
      return null
    } catch (error) {
      console.error('❌ ResidentApiService.getByEmail - Error al buscar residente por email:', error)
      return null
    }
  }

  /**
   * Actualizar residente
   */
  static async update(code: string, data: ResidentUpdate): Promise<ResidentResponse | null> {
    try {
      const resident = await apiClient.put<ResidentResponse>(`${this.BASE_URL}/${code}`, data)
      return resident
    } catch (error) {
      console.error('Error al actualizar residente:', error)
      return null
    }
  }
}

export { ResidentApiService }
