import { apiClient } from '@/core/config/axios.config'
import type { PathologistEditFormModel, PathologistUpdateRequest, PathologistUpdateResponse } from '../types/pathologist.types'

export interface PathologistEditResult {
  success: boolean
  data?: PathologistUpdateResponse
  error?: string
}

export const pathologistEditService = {
  async getByCode(code: string): Promise<PathologistEditResult> {
    try {
      const res = await apiClient.get(`/patologos/${code}`)
      // Normalizar la respuesta del backend (snake_case) al frontend (camelCase)
      const normalizedData = this.normalizePathologistData(res)
      return { success: true, data: normalizedData }
    } catch (e: any) {
      return { success: false, error: e.response?.data?.detail || e.message }
    }
  },

  async update(code: string, data: PathologistUpdateRequest): Promise<PathologistEditResult> {
    try {
      const res = await apiClient.put(`/patologos/${code}`, data)
      // Normalizar la respuesta del backend (snake_case) al frontend (camelCase)
      const normalizedData = this.normalizePathologistData(res)
      return { success: true, data: normalizedData }
    } catch (e: any) {
      return { success: false, error: e.response?.data?.detail || e.message }
    }
  },

  prepareUpdateData(form: PathologistEditFormModel): PathologistUpdateRequest {
    return {
      patologo_name: form.patologoName.trim(),
      iniciales_patologo: form.InicialesPatologo.trim(),
      patologo_email: form.PatologoEmail.trim(),
      registro_medico: form.registro_medico.trim(),
      observaciones: form.observaciones?.trim() || '',
      is_active: form.isActive,
      ...(form.password && form.password.trim().length >= 6 ? { password: form.password } : {})
    }
  },

  // Función para normalizar datos del backend (snake_case) al frontend (camelCase)
  normalizePathologistData(backendData: any): PathologistUpdateResponse {
    return {
      id: backendData.id || backendData._id,
      patologo_name: backendData.patologo_name,
      iniciales_patologo: backendData.iniciales_patologo,
      patologo_code: backendData.patologo_code,
      patologo_email: backendData.patologo_email,
      registro_medico: backendData.registro_medico,
      observaciones: backendData.observaciones || '',
      is_active: backendData.is_active,
      fecha_creacion: backendData.fecha_creacion,
      fecha_actualizacion: backendData.fecha_actualizacion
    }
  }
}

export default pathologistEditService


