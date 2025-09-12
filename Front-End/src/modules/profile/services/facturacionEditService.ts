import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { AxiosResponse } from 'axios'
import type { 
  FacturacionEditFormModel,
  FacturacionUpdateRequest,
  FacturacionUpdateResponse
} from '../types/facturacion.types'

export interface FacturacionEditResult {
  success: boolean
  data?: FacturacionUpdateResponse
  error?: string
}

class FacturacionEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.FACTURACION

  async getByCode(code: string): Promise<FacturacionEditResult> {
    try {
      const response: AxiosResponse<FacturacionUpdateResponse> = await apiClient.get<FacturacionUpdateResponse>(`${this.endpoint}/${code}`)
      return { success: true, data: response.data }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al obtener el usuario de facturación' 
      }
    }
  }

  async updateByCode(code: string, data: FacturacionUpdateRequest): Promise<FacturacionEditResult> {
    try {
      const response: AxiosResponse<FacturacionUpdateResponse> = await apiClient.put<FacturacionUpdateResponse>(`${this.endpoint}/${code}`, data)
      return { success: true, data: response.data }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al actualizar el usuario de facturación' 
      }
    }
  }

  prepareUpdateData(formModel: FacturacionEditFormModel): FacturacionUpdateRequest {
    return {
      facturacion_name: formModel.facturacionName,
      facturacion_email: formModel.FacturacionEmail,
      observaciones: formModel.observaciones,
      is_active: formModel.isActive,
      password: formModel.password || undefined
    }
  }

}

export const facturacionEditService = new FacturacionEditService()
