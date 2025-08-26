import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  AuxiliaryEditFormModel,
  AuxiliaryUpdateRequest,
  AuxiliaryUpdateResponse
} from '../types/auxiliary.types'

export interface AuxiliaryEditResult {
  success: boolean
  data?: AuxiliaryUpdateResponse
  error?: string
}

class AuxiliaryEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.AUXILIARIES

  async getByCode(code: string): Promise<AuxiliaryEditResult> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${code}`)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Error al obtener auxiliar' }
    }
  }

  async updateByCode(code: string, data: AuxiliaryUpdateRequest): Promise<AuxiliaryEditResult> {
    try {
      const response = await apiClient.put(`${this.endpoint}/${code}`, data)
      return { success: true, data: response }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar auxiliar'
      return { success: false, error: Array.isArray(errorMessage) ? errorMessage.join(', ') : errorMessage }
    }
  }

  prepareUpdateData(formModel: AuxiliaryEditFormModel): AuxiliaryUpdateRequest {
    return {
      auxiliarName: formModel.auxiliarName.trim(),
      AuxiliarEmail: formModel.AuxiliarEmail.trim(),
      observaciones: (formModel.observaciones || '').trim(),
      isActive: formModel.isActive,
      ...(formModel.password && formModel.password.trim().length >= 6 ? { password: formModel.password } : {})
    }
  }
}

export const auxiliaryEditService = new AuxiliaryEditService()
export default auxiliaryEditService


