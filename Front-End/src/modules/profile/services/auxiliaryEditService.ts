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
      // Normalizar la respuesta del backend (snake_case) al frontend (camelCase)
      const normalizedData = this.normalizeAuxiliaryData(response)
      return { success: true, data: normalizedData }
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Error al obtener auxiliar' }
    }
  }

  async updateByCode(code: string, data: AuxiliaryUpdateRequest): Promise<AuxiliaryEditResult> {
    try {
      const response = await apiClient.put(`${this.endpoint}/${code}`, data)
      // Normalizar la respuesta del backend (snake_case) al frontend (camelCase)
      const normalizedData = this.normalizeAuxiliaryData(response)
      return { success: true, data: normalizedData }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar auxiliar'
      return { success: false, error: Array.isArray(errorMessage) ? errorMessage.join(', ') : errorMessage }
    }
  }

  prepareUpdateData(formModel: AuxiliaryEditFormModel): AuxiliaryUpdateRequest {
    return {
      auxiliar_name: formModel.auxiliarName.trim(),
      auxiliar_email: formModel.AuxiliarEmail.trim(),
      observaciones: (formModel.observaciones || '').trim(),
      is_active: formModel.isActive,
      ...(formModel.password && formModel.password.trim().length >= 6 ? { password: formModel.password } : {})
    }
  }

  // Función para normalizar datos del backend (snake_case) al frontend (camelCase)
  private normalizeAuxiliaryData(backendData: any): AuxiliaryUpdateResponse {
    return {
      id: backendData.id || backendData._id,
      auxiliar_name: backendData.auxiliar_name,
      auxiliar_code: backendData.auxiliar_code,
      auxiliar_email: backendData.auxiliar_email,
      observaciones: backendData.observaciones || '',
      is_active: backendData.is_active,
      fecha_creacion: backendData.fecha_creacion,
      fecha_actualizacion: backendData.fecha_actualizacion
    }
  }
}

export const auxiliaryEditService = new AuxiliaryEditService()
export default auxiliaryEditService


