import type { EntityInfo } from '../types'
import { API_CONFIG, buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class EntitiesApiService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = buildApiUrl(endpoint)
    const defaultOptions: RequestInit = { headers: getAuthHeaders(), ...options }

    try {
      const response = await fetch(url, defaultOptions)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      throw error
    }
  }

  async getEntities(): Promise<EntityInfo[]> {
    try {
      const response = await this.makeRequest<any>(API_CONFIG.ENDPOINTS.ENTITIES)
      
      if (response.entidades && Array.isArray(response.entidades)) {
        return response.entidades.map((entity: any) => ({
          codigo: entity.entidad_code || '', nombre: entity.entidad_name || ''
        }))
      }
      
      return []
    } catch (error) {
      throw error
    }
  }

  async getEntityByCode(code: string): Promise<EntityInfo | null> {
    if (!code || code.trim() === '') return null
    
    try {
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/code/${code}`)
      
      if (response && response.entidad_code) {
        return { codigo: response.entidad_code, nombre: response.entidad_name }
      }
      
      return null
    } catch (error) {
      return null
    }
  }

  async searchEntities(query: string): Promise<EntityInfo[]> {
    try {
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}?query=${encodeURIComponent(query)}`)
      
      if (response.entidades && Array.isArray(response.entidades)) {
        return response.entidades.map((entity: any) => ({
          codigo: entity.entidad_code || '', nombre: entity.entidad_name || ''
        }))
      }
      
      return []
    } catch (error) {
      throw error
    }
  }
}

export const entitiesApiService = new EntitiesApiService()
