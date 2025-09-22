// Entities API: small fetch wrapper + mappers to normalized EntityInfo
import type { EntityInfo } from '../types'
import { API_CONFIG, buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class EntitiesApiService {
  // Generic GET using native fetch with auth headers
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = buildApiUrl(endpoint)
    const defaultOptions: RequestInit = { headers: getAuthHeaders(), ...options }
    const response = await fetch(url, defaultOptions)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error((errorData as any).detail || `HTTP error! status: ${response.status}`)
    }
    return await response.json()
  }

  // Map backend item to normalized EntityInfo
  private mapEntity = (e: any): EntityInfo => ({
    id: e?.entity_code || e?.code || e?.id || '',
    name: e?.name || e?.nombre || '',
    is_active: typeof e?.is_active === 'boolean' ? e.is_active : undefined
  }) as EntityInfo

  // Active entities only
  async getEntities(): Promise<EntityInfo[]> {
    const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}`)
    return Array.isArray(response) ? response.map(this.mapEntity) : []
  }

  // Active + inactive entities (includes activo flag)
  async getAllEntitiesIncludingInactive(): Promise<EntityInfo[]> {
    const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/inactive`)
    return Array.isArray(response) ? response.map(this.mapEntity) : []
  }

  async getEntityByCode(code: string): Promise<EntityInfo | null> {
    if (!code || code.trim() === '') return null
    try {
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/${encodeURIComponent(code)}`)
      return response ? this.mapEntity(response) : null
    } catch {
      return null
    }
  }

  async searchEntities(query: string, includeInactive: boolean = false): Promise<EntityInfo[]> {
    const endpoint = includeInactive
      ? `${API_CONFIG.ENDPOINTS.ENTITIES}/inactive?query=${encodeURIComponent(query)}`
      : `${API_CONFIG.ENDPOINTS.ENTITIES}?query=${encodeURIComponent(query)}`
    const response = await this.makeRequest<any>(endpoint)
    return Array.isArray(response) ? response.map(this.mapEntity) : []
  }
}

export const entitiesApiService = new EntitiesApiService()
