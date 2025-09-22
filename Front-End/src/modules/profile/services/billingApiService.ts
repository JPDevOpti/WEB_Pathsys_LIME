import apiClient from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface BillingResponse {
  id: string
  billing_code: string
  billing_name: string
  billing_email: string
  is_active: boolean
  observations?: string
  created_at: string
  updated_at: string
}

export interface BillingUpdate {
  billing_name?: string
  billing_email?: string
  is_active?: boolean
  observations?: string
}

class BillingApiService {
  private static readonly BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}/billing`

  /**
   * Obtener usuario de facturación por código
   */
  static async getByCode(code: string): Promise<BillingResponse | null> {
    try {
      const billing = await apiClient.get<BillingResponse>(`${this.BASE_URL}/${code}`)
      return billing
    } catch (error) {
      console.error('Error al obtener usuario de facturación:', error)
      return null
    }
  }

  /**
   * Buscar usuario de facturación por email
   */
  static async getByEmail(email: string): Promise<BillingResponse | null> {
    try {
      console.log('🔍 BillingApiService.getByEmail - Buscando usuario de facturación para:', email)
      const billingUsers = await apiClient.get<BillingResponse[]>(`${this.BASE_URL}/search`, {
        params: { q: email, limit: 1 }
      })
      
      console.log('📋 BillingApiService.getByEmail - Respuesta completa:', billingUsers)
      
      // El endpoint devuelve un array directamente
      if (Array.isArray(billingUsers) && billingUsers.length > 0) {
        console.log('✅ BillingApiService.getByEmail - Usuario de facturación encontrado:', billingUsers[0])
        return billingUsers[0] as BillingResponse
      }
      
      console.log('❌ BillingApiService.getByEmail - No se encontraron usuarios de facturación')
      return null
    } catch (error) {
      console.error('❌ BillingApiService.getByEmail - Error al buscar usuario de facturación por email:', error)
      return null
    }
  }

  /**
   * Actualizar usuario de facturación
   */
  static async update(code: string, data: BillingUpdate): Promise<BillingResponse | null> {
    try {
      const billing = await apiClient.put<BillingResponse>(`${this.BASE_URL}/${code}`, data)
      return billing
    } catch (error) {
      console.error('Error al actualizar usuario de facturación:', error)
      return null
    }
  }
}

export { BillingApiService }
