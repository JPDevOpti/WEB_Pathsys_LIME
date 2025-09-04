import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { FormPathologistInfo } from '../types'

export interface PathologistBackendResponse {
  id?: string
  _id?: string
  patologo_name: string
  iniciales_patologo?: string
  patologo_code: string
  patologo_email?: string
  registro_medico: string
  is_active?: boolean
  firma?: string
  observaciones?: string
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export class PathologistApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.PATHOLOGISTS

  async getPathologists(): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(`${this.endpoint}/search/active`, {
        params: { skip: 0, limit: 100 }
      })
      
      return this.transformPathologistsResponse(response)
    } catch (error: any) {
      throw new Error(`Error al obtener patólogos: ${error.message}`)
    }
  }

  async getAllPathologistsIncludingInactive(): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(`${this.endpoint}/search/all-including-inactive`, {
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

  async searchPathologists(query: string, includeInactive: boolean = false): Promise<FormPathologistInfo[]> {
    try {
      let endpoint: string
      
      if (includeInactive) {
        endpoint = `${this.endpoint}/search/all-including-inactive`
      } else {
        endpoint = `${this.endpoint}/search/active`
      }
      
      const response = await apiClient.get<PathologistBackendResponse[]>(endpoint, {
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
      id: pathologist.id || pathologist._id || pathologist.patologo_code || 'N/A',
      nombre: pathologist.patologo_name || 'Sin nombre',
      iniciales: pathologist.iniciales_patologo || this.generateInitials(pathologist.patologo_name),
      documento: pathologist.patologo_code || 'N/A',
      email: pathologist.patologo_email || '',
      medicalLicense: pathologist.registro_medico || 'N/A',
      isActive: pathologist.is_active ?? true
    }
  }
}

export const pathologistApiService = new PathologistApiService()
export default pathologistApiService
