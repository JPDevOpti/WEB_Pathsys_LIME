import { apiClient } from '@/core/config/axios.config'
import type { AxiosResponse } from 'axios'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  BillingCreateRequest, 
  BillingCreateResponse 
} from '../types/billing.types'

class BillingCreateService {
  private readonly facturacionEndpoint = API_CONFIG.ENDPOINTS.FACTURACION
  private readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  private trimOrEmpty = (v?: string) => (v ?? '').toString().trim()
  private isEmailValid = (email: string) => this.EMAIL_REGEX.test(email)

  async createFacturacion(facturacionData: BillingCreateRequest): Promise<BillingCreateResponse> {
    try {
      const payload: BillingCreateRequest = {
        billing_name: this.trimOrEmpty(facturacionData.billing_name),
        billing_code: this.trimOrEmpty(facturacionData.billing_code),
        billing_email: this.trimOrEmpty(facturacionData.billing_email),
        password: this.trimOrEmpty(facturacionData.password),
        observations: this.trimOrEmpty(facturacionData.observations),
        is_active: !!facturacionData.is_active
      }

      const response: AxiosResponse<BillingCreateResponse> = await apiClient.post<BillingCreateResponse>(
        `${this.facturacionEndpoint}/`,
        payload
      )

      return (response as any).data ?? (response as any)
    } catch (error: any) {
      console.error('Error creating facturacion:', error)
      
      if (error.response?.status === 409) {
        const detail = error.response.data?.detail || 'Ya existe un usuario de facturación con estos datos'
        throw new Error(detail)
      } else if (error.response?.status === 422) {
        throw new Error('Los datos proporcionados no son válidos')
      } else if (error.response?.status === 400) {
        throw new Error('Datos incorrectos o incompletos')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else if (error.message) {
        throw new Error(`Error del servidor: ${error.message}`)
      } else {
        throw new Error('Error interno del servidor. Inténtelo más tarde')
      }
    }
  }

  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const normalized = this.trimOrEmpty(email)
      if (!normalized) return false
      const response = await apiClient.get(
        `${this.facturacionEndpoint}/search?billing_email=${encodeURIComponent(normalized)}`
      )
      const list = Array.isArray(response) ? response : (response as any)?.data
      return Array.isArray(list) && list.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return false
    }
  }

  validateFacturacionData(data: BillingCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    const name = this.trimOrEmpty(data.billing_name)
    const code = this.trimOrEmpty(data.billing_code)
    const email = this.trimOrEmpty(data.billing_email)
    const password = this.trimOrEmpty(data.password)
    const observations = this.trimOrEmpty(data.observations)

    if (!name) errors.push('El nombre es requerido')
    else if (name.length < 2) errors.push('El nombre debe tener al menos 2 caracteres')
    else if (name.length > 200) errors.push('El nombre no puede exceder 200 caracteres')

    if (!code) errors.push('El código es requerido')
    else if (code.length < 3) errors.push('El código debe tener al menos 3 caracteres')
    else if (code.length > 20) errors.push('El código no puede exceder 20 caracteres')

    if (!email) errors.push('El email es requerido')
    else if (!this.isEmailValid(email)) errors.push('El email no tiene un formato válido')

    if (!password) errors.push('La contraseña es requerida')
    else if (password.length < 6) errors.push('La contraseña debe tener al menos 6 caracteres')
    else if (password.length > 128) errors.push('La contraseña no puede exceder 128 caracteres')

    if (observations && observations.length > 500) errors.push('Las observaciones no pueden exceder 500 caracteres')

    return { isValid: errors.length === 0, errors }
  }
}

export const billingCreateService = new BillingCreateService()
