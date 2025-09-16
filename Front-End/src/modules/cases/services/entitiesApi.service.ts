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
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}`)
      if (Array.isArray(response)) {
        return response.map((e: any) => ({ codigo: e.entity_code || e.code || '', nombre: e.name || '' }))
      }
      return []
    } catch (error) {
      throw error
    }
  }

  async getAllEntitiesIncludingInactive(): Promise<EntityInfo[]> {
    try {
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/inactive`)
      if (Array.isArray(response)) {
        return response.map((e: any) => ({ codigo: e.entity_code || e.code || '', nombre: e.name || '', activo: e.is_active }))
      }
      return []
    } catch (error) {
      throw error
    }
  }

  async getEntityByCode(code: string): Promise<EntityInfo | null> {
    if (!code || code.trim() === '') return null
    
    try {
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/${encodeURIComponent(code)}`)
      if (response && (response.entity_code || response.code)) {
        return { codigo: response.entity_code || response.code, nombre: response.name || '' }
      }
      return null
    } catch (error) {
      return null
    }
  }

  async searchEntities(query: string, includeInactive: boolean = false): Promise<EntityInfo[]> {
    try {
      const endpoint = includeInactive
        ? `${API_CONFIG.ENDPOINTS.ENTITIES}/inactive?query=${encodeURIComponent(query)}`
        : `${API_CONFIG.ENDPOINTS.ENTITIES}?query=${encodeURIComponent(query)}`
      const response = await this.makeRequest<any>(endpoint)
      if (Array.isArray(response)) {
        return response.map((e: any) => ({ codigo: e.entity_code || e.code || '', nombre: e.name || '', activo: e.is_active }))
      }
      return []
    } catch (error) {
      throw error
    }
  }
}

export const entitiesApiService = new EntitiesApiService()
