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

  /**
   * Obtener auxiliar por código
   */
  static async getByCode(code: string): Promise<AuxiliarResponse | null> {
    try {
      const auxiliar = await apiClient.get<AuxiliarResponse>(`${this.BASE_URL}/${code}`)
      return auxiliar
    } catch (error) {
      console.error('Error al obtener auxiliar:', error)
      return null
    }
  }

  /**
   * Buscar auxiliar por email
   */
  static async getByEmail(email: string): Promise<AuxiliarResponse | null> {
    try {
      console.log('🔍 AuxiliarApiService.getByEmail - Buscando auxiliar para:', email)
      const auxiliaries = await apiClient.get<AuxiliarResponse[]>(`${this.BASE_URL}/search`, {
        params: { auxiliar_email: email, limit: 1 }
      })
      
      console.log('📋 AuxiliarApiService.getByEmail - Respuesta completa:', auxiliaries)
      
      // El endpoint devuelve un array directamente
      if (Array.isArray(auxiliaries) && auxiliaries.length > 0) {
        console.log('✅ AuxiliarApiService.getByEmail - Auxiliar encontrado:', auxiliaries[0])
        return auxiliaries[0] as AuxiliarResponse
      }
      
      console.log('❌ AuxiliarApiService.getByEmail - No se encontraron auxiliares')
      return null
    } catch (error) {
      console.error('❌ AuxiliarApiService.getByEmail - Error al buscar auxiliar por email:', error)
      return null
    }
  }

  /**
   * Actualizar auxiliar
   */
  static async update(code: string, data: AuxiliarUpdate): Promise<AuxiliarResponse | null> {
    try {
      const auxiliar = await apiClient.put<AuxiliarResponse>(`${this.BASE_URL}/${code}`, data)
      return auxiliar
    } catch (error) {
      console.error('Error al actualizar auxiliar:', error)
      return null
    }
  }
}

export { AuxiliarApiService }
