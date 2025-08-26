import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { EntityEditFormModel, EntityUpdateRequest, EntityUpdateResponse } from '../types/entity.types'

class EntityEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  async getByCode(code: string): Promise<EntityEditFormModel> {
    const response = await apiClient.get<EntityUpdateResponse>(`${this.endpoint}/code/${code}`)
    return {
      id: response.id,
      EntidadName: response.EntidadName,
      EntidadCode: response.EntidadCode,
      observaciones: response.observaciones,
      isActive: response.isActive
    }
  }

  async updateByCode(originalCode: string, data: EntityUpdateRequest): Promise<EntityUpdateResponse> {
    return await apiClient.put<EntityUpdateResponse>(`${this.endpoint}/code/${originalCode}`, data)
  }

  async checkCodeExists(code: string, originalCode?: string): Promise<boolean> {
    if (originalCode && code === originalCode) return false
    try {
      await apiClient.get(`${this.endpoint}/code/${code}`)
      return true
    } catch (error: any) {
      if (error.response?.status === 404) return false
      return true
    }
  }

  prepareUpdateData(original: EntityEditFormModel, current: EntityEditFormModel): EntityUpdateRequest {
    const update: EntityUpdateRequest = {}
    if (original.EntidadName !== current.EntidadName) update.EntidadName = current.EntidadName
    if (original.EntidadCode !== current.EntidadCode) update.EntidadCode = current.EntidadCode
    if (original.observaciones !== current.observaciones) update.observaciones = current.observaciones
    if (original.isActive !== current.isActive) update.isActive = current.isActive
    return update
  }
}

export const entityEditService = new EntityEditService()
export default entityEditService


