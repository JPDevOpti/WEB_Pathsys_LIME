// Pathologists API: typed fetchers + response mappers
import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { FormPathologistInfo } from '../types'

export interface PathologistBackendResponse {
  id?: string
  _id?: string
  pathologist_name: string
  initials?: string
  pathologist_code: string
  pathologist_email?: string
  medical_license: string
  is_active?: boolean
  signature?: string
  observations?: string
  created_at?: string
  updated_at?: string
}

export class PathologistApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.PATHOLOGISTS
  private readonly defaultLimit = 100

  // Map one backend item to unified UI type
  private transformPathologistResponse(pathologist: PathologistBackendResponse): FormPathologistInfo {
    return {
      id: pathologist.id || pathologist._id || pathologist.pathologist_code || 'N/A',
      patologo_code: pathologist.pathologist_code,
      patologo_name: pathologist.pathologist_name,
      nombre: pathologist.pathologist_name || 'Sin nombre',
      iniciales: pathologist.initials || this.generateInitials(pathologist.pathologist_name),
      documento: pathologist.pathologist_code || 'N/A',
      email: pathologist.pathologist_email || '',
      medicalLicense: pathologist.medical_license || 'N/A',
      isActive: pathologist.is_active ?? true
    }
  }

  // Map list
  private transformPathologistsResponse(pathologists: PathologistBackendResponse[]): FormPathologistInfo[] {
    return pathologists.map(p => this.transformPathologistResponse(p))
  }

  // Generic GET wrapper with unified error
  private async getClean<T>(url: string, params?: any): Promise<T> {
    try { return await apiClient.get<T>(url, params ? { params } : undefined) }
    catch (error: any) { throw new Error(error.message || `Error GET ${url}`) }
  }

  async getPathologists(): Promise<FormPathologistInfo[]> {
    const response = await this.getClean<PathologistBackendResponse[]>(`${this.endpoint}/`, { skip: 0, limit: this.defaultLimit })
    return this.transformPathologistsResponse(response)
  }

  async getAllPathologistsIncludingInactive(): Promise<FormPathologistInfo[]> {
    const response = await this.getClean<PathologistBackendResponse[]>(`${this.endpoint}/search`, { skip: 0, limit: this.defaultLimit })
    return this.transformPathologistsResponse(response)
  }

  async getPathologist(id: string): Promise<FormPathologistInfo> {
    const response = await this.getClean<PathologistBackendResponse>(`${this.endpoint}/${id}`)
    return this.transformPathologistResponse(response)
  }

  async getPathologistById(id: string): Promise<FormPathologistInfo | null> {
    try { return await this.getPathologist(id) } catch { return null }
  }

  async searchPathologists(query: string, includeInactive: boolean = false): Promise<FormPathologistInfo[]> {
    try {
      const params: any = { q: query }
      if (includeInactive) params.include_inactive = true
      const response = await this.getClean<PathologistBackendResponse[]>(`${this.endpoint}/search`, params)
      return this.transformPathologistsResponse(response)
    } catch {
      return []
    }
  }

  // Compute initials from full name (skip common prefixes)
  private generateInitials(fullName?: string): string {
    if (!fullName || typeof fullName !== 'string' || fullName.trim().length === 0) return 'N/A'
    
    const nameClean = fullName.replace(/\b(Dr\.?|Dra\.?|Doctor|Doctora)\b\s*/gi, '')
    const words = nameClean.trim().split(/\s+/)
    const initials = words
      .filter(word => word.length > 0)
      .map(word => word[0].toUpperCase())
      .join('')
    
    return initials.slice(0, 10) || 'N/A'
  }
}

export const pathologistApiService = new PathologistApiService()
export default pathologistApiService
