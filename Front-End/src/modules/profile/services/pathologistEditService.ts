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
      return { success: true, data: res }
    } catch (e: any) {
      return { success: false, error: e.response?.data?.detail || e.message }
    }
  },

  async update(code: string, data: PathologistUpdateRequest): Promise<PathologistEditResult> {
    try {
      const res = await apiClient.put(`/patologos/${code}`, data)
      return { success: true, data: res }
    } catch (e: any) {
      return { success: false, error: e.response?.data?.detail || e.message }
    }
  },

  prepareUpdateData(form: PathologistEditFormModel): PathologistUpdateRequest {
    return {
      patologoName: form.patologoName.trim(),
      InicialesPatologo: form.InicialesPatologo.trim(),
      PatologoEmail: form.PatologoEmail.trim(),
      registro_medico: form.registro_medico.trim(),
      observaciones: form.observaciones?.trim() || '',
      isActive: form.isActive,
      ...(form.password && form.password.trim().length >= 6 ? { password: form.password } : {})
    }
  }
}

export default pathologistEditService


