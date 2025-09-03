import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { EntityEditFormModel, EntityUpdateRequest, EntityUpdateResponse } from '../types/entity.types'

class EntityEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  async getByCode(code: string): Promise<EntityEditFormModel> {
    const response = await apiClient.get<EntityUpdateResponse>(`${this.endpoint}/code/${code}`)
    return {
      id: response.id,
      EntidadName: response.entidad_name,
      EntidadCode: response.entidad_code,
      observaciones: response.observaciones,
      isActive: response.is_active
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
}

export const entityEditService = new EntityEditService()
export default entityEditService


