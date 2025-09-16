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

  async getPathologists(): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(`${this.endpoint}/`, {
        params: { skip: 0, limit: 100 }
      })
      
      return this.transformPathologistsResponse(response)
    } catch (error: any) {
      throw new Error(`Error al obtener patólogos: ${error.message}`)
    }
  }

  async getAllPathologistsIncludingInactive(): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(`${this.endpoint}/search`, {
        params: { skip: 0, limit: 100 }
      })
      
      return this.transformPathologistsResponse(response)
    } catch (error: any) {
      throw new Error(`Error al obtener todos los patólogos: ${error.message}`)
    }
  }

  async getPathologist(id: string): Promise<FormPathologistInfo> {
    try {
      const response = await apiClient.get<PathologistBackendResponse>(`${this.endpoint}/${id}`)
      return this.transformPathologistResponse(response)
    } catch (error: any) {
      throw new Error(`Error al obtener patólogo: ${error.message}`)
    }
  }

  async getPathologistById(id: string): Promise<FormPathologistInfo | null> {
    try {
      const response = await apiClient.get<PathologistBackendResponse>(`${this.endpoint}/${id}`)
      return this.transformPathologistResponse(response)
    } catch (error: any) {
      console.warn(`Patólogo con ID ${id} no encontrado:`, error.message)
      return null
    }
  }

  async searchPathologists(query: string, includeInactive: boolean = false): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(`${this.endpoint}/search`, {
        params: { q: query }
      })
      
      return this.transformPathologistsResponse(response)
    } catch (error: any) {
      return []
    }
  }

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

  private transformPathologistsResponse(pathologists: PathologistBackendResponse[]): FormPathologistInfo[] {
    return pathologists.map(pathologist => this.transformPathologistResponse(pathologist))
  }

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
}

export const pathologistApiService = new PathologistApiService()
export default pathologistApiService
