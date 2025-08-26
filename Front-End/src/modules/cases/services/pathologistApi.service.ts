import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { FormPathologistInfo } from '../types'

/**
 * Respuesta del backend para lista de patólogos
 */
export interface PathologistBackendResponse {
  id?: string
  _id?: string
  patologoName: string
  InicialesPatologo?: string
  patologoCode: string
  PatologoEmail?: string
  registro_medico: string
  isActive?: boolean
  firma?: string
  observaciones?: string
  fecha_creacion?: string
  fecha_actualizacion?: string
}

/**
 * Servicio para operaciones con patólogos
 */
export class PathologistApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.PATHOLOGISTS

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Obtiene la lista de todos los patólogos activos
   * @returns Lista de patólogos
   */
  async getPathologists(): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(this.endpoint, {
        params: {
          skip: 0,
          limit: 100 // Obtener hasta 100 patólogos activos
        }
      })
      
      return this.transformPathologistsResponse(response)
    } catch (error: any) {
      console.error('Error al obtener patólogos:', error)
      throw new Error(error.message || 'Error al obtener la lista de patólogos')
    }
  }

  /**
   * Obtiene un patólogo específico por ID
   * @param id - ID del patólogo
   * @returns Información del patólogo
   */
  async getPathologist(id: string): Promise<FormPathologistInfo> {
    try {
      const response = await apiClient.get<PathologistBackendResponse>(`${this.endpoint}/${id}`)
      return this.transformPathologistResponse(response)
    } catch (error: any) {
      console.error(`Error al obtener patólogo ${id}:`, error)
      throw new Error(error.message || `Error al obtener el patólogo ${id}`)
    }
  }

  /**
   * Busca patólogos por nombre o documento
   * @param query - Término de búsqueda
   * @returns Lista de patólogos que coinciden con la búsqueda
   */
  async searchPathologists(query: string): Promise<FormPathologistInfo[]> {
    try {
      const response = await apiClient.get<PathologistBackendResponse[]>(`${this.endpoint}/buscar`, {
        params: { query }
      })
      
      return this.transformPathologistsResponse(response)
    } catch (error: any) {
      console.error(`Error al buscar patólogos con query "${query}":`, error)
      // En caso de error, devolver lista vacía en lugar de lanzar excepción
      return []
    }
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Genera iniciales a partir del nombre completo
   * @param fullName - Nombre completo del patólogo
   * @returns Iniciales generadas
   */
  private generateInitials(fullName: string): string {
    // Remover títulos comunes
    const nameClean = fullName.replace(/\b(Dr\.?|Dra\.?|Doctor|Doctora)\b\s*/gi, '')
    
    // Dividir en palabras y tomar la primera letra de cada una
    const words = nameClean.trim().split(/\s+/)
    const initials = words
      .filter(word => word.length > 0)
      .map(word => word[0].toUpperCase())
      .join('')
    
    // Limitar a máximo 10 caracteres
    return initials.slice(0, 10) || 'N/A'
  }

  /**
   * Transforma la respuesta del backend al formato del frontend
   * @param pathologists - Lista de patólogos del backend
   * @returns Lista de patólogos transformada
   */
  private transformPathologistsResponse(pathologists: PathologistBackendResponse[]): FormPathologistInfo[] {
    return pathologists.map(pathologist => this.transformPathologistResponse(pathologist))
  }

  /**
   * Transforma un patólogo del backend al formato del frontend
   * @param pathologist - Patólogo del backend
   * @returns Patólogo transformado
   */
  private transformPathologistResponse(pathologist: PathologistBackendResponse): FormPathologistInfo {
    return {
      id: pathologist.id || pathologist._id || pathologist.patologoCode,
      nombre: pathologist.patologoName,
      iniciales: pathologist.InicialesPatologo || this.generateInitials(pathologist.patologoName),
      documento: pathologist.patologoCode,
      email: pathologist.PatologoEmail || '',
      medicalLicense: pathologist.registro_medico,
      isActive: pathologist.isActive ?? true
    }
  }
}

// Exportar instancia singleton
export const pathologistApiService = new PathologistApiService()
export default pathologistApiService
