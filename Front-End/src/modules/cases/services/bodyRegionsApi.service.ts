import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface BodyRegionItem {
  value: string
  label: string
  category?: string
}

class BodyRegionsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.BODY_REGIONS

  async getAll(): Promise<BodyRegionItem[]> {
    const response = await apiClient.get(`${this.endpoint}/`)
    const data = response.data
    if (Array.isArray(data)) return data as BodyRegionItem[]
    if (Array.isArray(data?.items)) return data.items as BodyRegionItem[]
    return []
  }
}

export const bodyRegionsApiService = new BodyRegionsApiService()


