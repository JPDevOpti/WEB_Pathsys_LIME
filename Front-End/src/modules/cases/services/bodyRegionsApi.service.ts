import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface BodyRegionItem {
  value: string
  label: string
  category?: string
}

class BodyRegionsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES

  async getAll(): Promise<BodyRegionItem[]> {
    const response = await apiClient.get(`${this.endpoint}/body-regions`)
    const data = response.data
    return Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
  }
}

export const bodyRegionsApiService = new BodyRegionsApiService()


