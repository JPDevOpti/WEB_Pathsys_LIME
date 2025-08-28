import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { FormPathologistInfo } from '../types'

/**
 * Respuesta del backend para lista de patólogos
 */
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
      throw new Error(`Error al obtener patólogos: ${error.message}`)
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
      throw new Error(`Error al obtener patólogo: ${error.message}`)
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
  private generateInitials(fullName?: string): string {
    // Validar que fullName exista y no esté vacío
    if (!fullName || typeof fullName !== 'string' || fullName.trim().length === 0) {
      return 'N/A'
    }
    
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
    // Validar campos requeridos
    if (!pathologist.patologo_name || !pathologist.patologo_code) {
      // Patólogo con datos incompletos, usar valores por defecto
    }
    
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

// Exportar instancia singleton
export const pathologistApiService = new PathologistApiService()
export default pathologistApiService
