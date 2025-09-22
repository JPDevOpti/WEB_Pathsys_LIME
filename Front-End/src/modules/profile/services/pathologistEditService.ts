import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PathologistEditFormModel, PathologistUpdateRequest, PathologistUpdateResponse } from '../types/pathologist.types'

export interface PathologistEditResult {
  success: boolean
  data?: PathologistUpdateResponse
  error?: string
}

export const pathologistEditService = {
  async getByCode(code: string): Promise<PathologistEditResult> {
    try {
      const res = await apiClient.get(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${code}`)
      // Normalizar la respuesta del backend (snake_case) al frontend (camelCase)
      const normalizedData = this.normalizePathologistData(res)
      return { success: true, data: normalizedData }
    } catch (e: any) {
      return { success: false, error: e.response?.data?.detail || e.message }
    }
  },

  async update(code: string, data: PathologistUpdateRequest): Promise<PathologistEditResult> {
    try {
      const res = await apiClient.put(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${code}`, data)
      // Normalizar la respuesta del backend (snake_case) al frontend (camelCase)
      const normalizedData = this.normalizePathologistData(res)
      return { success: true, data: normalizedData }
    } catch (e: any) {
      return { success: false, error: e.response?.data?.detail || e.message }
    }
  },

  prepareUpdateData(form: PathologistEditFormModel): PathologistUpdateRequest {
    return {
      pathologist_name: form.patologoName.trim(),
      initials: form.InicialesPatologo.trim(),
      pathologist_email: form.PatologoEmail.trim(),
      medical_license: form.registro_medico.trim(),
      observations: form.observaciones?.trim() || '',
      is_active: form.isActive,
      ...(form.password && form.password.trim().length >= 6 ? { password: form.password } : {})
    }
  },

  // Función para normalizar datos del backend (snake_case) al frontend (camelCase)
  normalizePathologistData(backendData: any): PathologistUpdateResponse {
    return {
      id: backendData.id || backendData._id,
      pathologist_name: backendData.pathologist_name,
      initials: backendData.initials,
      pathologist_code: backendData.pathologist_code,
      pathologist_email: backendData.pathologist_email,
      medical_license: backendData.medical_license,
      observations: backendData.observations || '',
      is_active: backendData.is_active,
      created_at: backendData.created_at,
      updated_at: backendData.updated_at
    }
  }
}

export default pathologistEditService


