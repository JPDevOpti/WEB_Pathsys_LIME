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
  private static readonly logPrefix = '[BillingApiService]'

  private static trimOrEmpty(value?: string) {
    return (value ?? '').toString().trim()
  }

  /**
   * Obtener usuario de facturación por código
   */
  static async getByCode(code: string): Promise<BillingResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return null
      const billing = await apiClient.get<BillingResponse>(`${this.BASE_URL}/${normalized}`)
      return billing
    } catch (error) {
      console.error(`${this.logPrefix} getByCode error:`, error)
      return null
    }
  }

  /**
   * Buscar usuario de facturación por email
   */
  static async getByEmail(email: string): Promise<BillingResponse | null> {
    try {
      const normalized = this.trimOrEmpty(email)
      if (!normalized) return null
      const billingUsers = await apiClient.get<BillingResponse[]>(`${this.BASE_URL}/search`, {
        params: { q: normalized, limit: 1 }
      })
      return Array.isArray(billingUsers) && billingUsers.length > 0 ? billingUsers[0] : null
    } catch (error) {
      console.error(`${this.logPrefix} getByEmail error:`, error)
      return null
    }
  }

  /**
   * Actualizar usuario de facturación
   */
  static async update(code: string, data: BillingUpdate): Promise<BillingResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return null
      const billing = await apiClient.put<BillingResponse>(`${this.BASE_URL}/${normalized}`, data)
      return billing
    } catch (error) {
      console.error(`${this.logPrefix} update error:`, error)
      return null
    }
  }
}

export { BillingApiService }
