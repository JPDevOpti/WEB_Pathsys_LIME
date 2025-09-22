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

  async getByCode(code: string): Promise<FacturacionEditResult> {
    try {
      const response: AxiosResponse<BillingUpdateResponse> = await apiClient.get<BillingUpdateResponse>(`${this.endpoint}/${code}`)
      return { success: true, data: response.data }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al obtener el usuario de facturación' 
      }
    }
  }

  async updateByCode(code: string, data: BillingUpdateRequest): Promise<FacturacionEditResult> {
    try {
      const response: AxiosResponse<BillingUpdateResponse> = await apiClient.put<BillingUpdateResponse>(`${this.endpoint}/${code}`, data)
      return { success: true, data: response.data }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al actualizar el usuario de facturación' 
      }
    }
  }

  prepareUpdateData(formModel: BillingEditFormModel): BillingUpdateRequest {
    return {
      billing_name: formModel.facturacionName,
      billing_email: formModel.FacturacionEmail,
      observations: formModel.observaciones,
      is_active: formModel.isActive,
      password: formModel.password || undefined
    }
  }
}

export const billingEditService = new BillingEditService()
