import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { AxiosResponse } from 'axios'
import type {
  BillingEditFormModel,
  BillingUpdateRequest,
  BillingUpdateResponse
} from '../types/billing.types'

export interface FacturacionEditResult {
  success: boolean
  data?: BillingUpdateResponse
  error?: string
}

class BillingEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.FACTURACION
  private trimOrEmpty = (v?: string) => (v ?? '').toString().trim()

  // Obtener usuario de facturación por código
  async getByCode(code: string): Promise<FacturacionEditResult> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return { success: false, error: 'Código inválido' }
      const response: AxiosResponse<BillingUpdateResponse> | BillingUpdateResponse = await apiClient.get<BillingUpdateResponse>(`${this.endpoint}/${normalized}`)
      const data = (response as any).data ?? (response as any)
      return { success: true, data }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al obtener el usuario de facturación' 
      }
    }
  }

  // Actualizar usuario de facturación por código
  async updateByCode(code: string, data: BillingUpdateRequest): Promise<FacturacionEditResult> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return { success: false, error: 'Código inválido' }
      const response: AxiosResponse<BillingUpdateResponse> | BillingUpdateResponse = await apiClient.put<BillingUpdateResponse>(`${this.endpoint}/${normalized}`, data)
      const payload = (response as any).data ?? (response as any)
      return { success: true, data: payload }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al actualizar el usuario de facturación' 
      }
    }
  }

  // Preparar payload de actualización desde el formulario de edición (camelCase -> snake_case)
  prepareUpdateData(formModel: BillingEditFormModel): BillingUpdateRequest {
    const billing_name = this.trimOrEmpty((formModel as any).billingName ?? (formModel as any).facturacionName)
    const billing_email = this.trimOrEmpty((formModel as any).billingEmail ?? (formModel as any).FacturacionEmail)
    const observations = this.trimOrEmpty((formModel as any).observations ?? (formModel as any).observaciones)
    const is_active = !!formModel.isActive
    const password = this.trimOrEmpty(formModel.password)

    const payload: BillingUpdateRequest = {
      billing_name,
      billing_email,
      observations,
      is_active,
      ...(password ? { password } : {})
    }
    return payload
  }
}

export const billingEditService = new BillingEditService()
