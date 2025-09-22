import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { EntityCreateRequest, EntityCreateResponse } from '../types/entity.types'

const CODE_REGEX = /^[A-Z0-9_-]+$/i

class EntityCreateService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  async createEntity(entityData: EntityCreateRequest): Promise<EntityCreateResponse> {
    try {
      const response = await apiClient.post<EntityCreateResponse>(`${this.endpoint}/`, entityData)
      return response
    } catch (error: any) {
      if (error.response?.status === 409) {
        const errorMessage = error.response.data?.detail || error.message || 'Duplicate data'
        const customError = new Error(errorMessage) as any
        customError.response = error.response
        throw customError
      } else if (error.response?.status === 400) {
        throw new Error(error.message || 'An entity with this code already exists')
      } else if (error.response?.status === 422) {
        const validationErrors = error.response.data?.detail
        if (Array.isArray(validationErrors)) {
          const errorMessages = validationErrors.map((err: any) => {
            const field = err.loc?.[err.loc.length - 1] || 'field'
            return `${field}: ${err.msg}`
          }).join(', ')
          throw new Error(`Validation errors: ${errorMessages}`)
        }
        throw new Error('Invalid form data')
      } else {
        throw new Error(error.message || 'Error creating entity')
      }
    }
  }

  async checkCodeExists(entityCode: string): Promise<boolean> {
    try {
      await apiClient.get(`${this.endpoint}/${entityCode}`)
      return true
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return true
    }
  }

  validateEntityData(data: Partial<EntityCreateRequest>): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!data.name?.trim()) {
      errors.push('Entity name is required')
    } else if (data.name.length < 2) {
      errors.push('Name must have at least 2 characters')
    } else if (data.name.length > 200) {
      errors.push('Name cannot exceed 200 characters')
    }

    if (!data.entity_code?.trim()) {
      errors.push('Entity code is required')
    } else if (data.entity_code.length < 2) {
      errors.push('Code must have at least 2 characters')
    } else if (data.entity_code.length > 20) {
      errors.push('Code cannot exceed 20 characters')
    } else if (!CODE_REGEX.test(data.entity_code)) {
      errors.push('Code can only contain letters, numbers, hyphens and underscores')
    }

    if (data.notes && data.notes.length > 500) {
      errors.push('Notes cannot exceed 500 characters')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

export const entityCreateService = new EntityCreateService()
export default entityCreateService
