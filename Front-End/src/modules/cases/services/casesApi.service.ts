import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  CaseModel,
  CaseListResponse,
  CaseSearchResponse,
  CaseStatisticsResponse,
  CreateCaseRequest,
  CreateCaseResponse,
  UpdateCaseRequest,
  UpdateCaseResponse,
  DeleteCaseResponse,
  CaseSearchParams,
  CaseListParams
} from '../types'

/**
 * Servicio para operaciones CRUD de casos médicos
 */
export class CasesApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES

  // ============================================================================
  // FUNCIONES DE CONSULTA
  // ============================================================================

  /**
   * Consulta el siguiente consecutivo disponible (sin consumirlo)
   * @returns Información del consecutivo disponible
   */
  async consultarConsecutivo(): Promise<{ codigo_consecutivo: string; mensaje: string }> {
    try {
      const response = await apiClient.get<{ codigo_consecutivo: string; mensaje: string }>(`${this.endpoint}/siguiente-consecutivo`)
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al consultar el consecutivo')
    }
  }

  /**
   * Obtiene la lista de casos con paginación
   * @param params - Parámetros de paginación y filtros
   * @returns Lista de casos
   */
  async getCases(params: CaseListParams = {}): Promise<CaseListResponse> {
    try {
      const response = await apiClient.get<CaseListResponse>(this.endpoint, { params })
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener la lista de casos')
    }
  }

  /**
   * Obtiene un caso específico por código
   * @param caseCode - Código del caso
   * @returns Información del caso
   */
  async getCaseByCode(caseCode: string): Promise<CaseModel> {
    try {
      const response = await apiClient.get<CaseModel>(`${this.endpoint}/caso-code/${caseCode}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener el caso ${caseCode}`)
    }
  }

  /**
   * Obtiene casos por paciente
   * @param cedula - Cédula del paciente
   * @returns Lista de casos del paciente
   */
  async getCasesByPatient(cedula: string): Promise<CaseModel[]> {
    try {
      const response = await apiClient.get<CaseModel[]>(`${this.endpoint}/paciente/${cedula}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener casos del paciente ${cedula}`)
    }
  }

  /**
   * Obtiene casos por patólogo
   * @param codigo - Código del patólogo
   * @returns Lista de casos del patólogo
   */
  async getCasesByPathologist(codigo: string): Promise<CaseListResponse> {
    try {
      const response = await apiClient.get<CaseListResponse>(`${this.endpoint}/patologo/${codigo}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener casos del patólogo ${codigo}`)
    }
  }

  /**
   * Obtiene casos por estado
   * @param estado - Estado de los casos
   * @returns Lista de casos con el estado especificado
   */
  async getCasesByState(estado: string): Promise<CaseListResponse> {
    try {
      const response = await apiClient.get<CaseListResponse>(`${this.endpoint}/estado/${estado}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener casos con estado ${estado}`)
    }
  }

  /**
   * Obtiene estadísticas del sistema
   * @returns Estadísticas de casos
   */
  async getCaseStatistics(): Promise<CaseStatisticsResponse> {
    try {
      const response = await apiClient.get<CaseStatisticsResponse>(`${this.endpoint}/estadisticas`)
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener estadísticas del sistema')
    }
  }

  // ============================================================================
  // FUNCIONES DE BÚSQUEDA
  // ============================================================================

  /**
   * Realiza búsqueda avanzada de casos
   * @param searchParams - Parámetros de búsqueda
   * @returns Resultados de la búsqueda
   */
  async searchCases(searchParams: CaseSearchParams): Promise<CaseSearchResponse> {
    try {
      const response = await apiClient.post<CaseSearchResponse>(`${this.endpoint}/buscar`, searchParams)
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al buscar casos')
    }
  }

  /**
   * Realiza búsqueda con filtros avanzados usando query parameters
   * @param searchParams - Parámetros de búsqueda
   * @returns Resultados de la búsqueda
   */
  async searchCasesAdvanced(searchParams: CaseSearchParams): Promise<CaseSearchResponse> {
    try {
      const response = await apiClient.get<CaseSearchResponse>(`${this.endpoint}/search`, { params: searchParams })
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error en la búsqueda avanzada')
    }
  }

  // ============================================================================
  // FUNCIONES DE CREACIÓN Y MODIFICACIÓN
  // ============================================================================

  /**
   * Crea un nuevo caso médico
   * @param caseData - Datos del caso a crear
   * @returns Caso creado
   */
  async createCase(caseData: CreateCaseRequest): Promise<CreateCaseResponse> {
    try {
      const response = await apiClient.post<CreateCaseResponse>(this.endpoint, caseData)
      return response
    } catch (error: any) {
      throw this.handleValidationError(error)
    }
  }

  /**
   * Actualiza un caso existente
   * @param caseCode - Código del caso
   * @param updateData - Datos de actualización
   * @returns Caso actualizado
   */
  async updateCase(caseCode: string, updateData: UpdateCaseRequest): Promise<UpdateCaseResponse> {
    try {
      const response = await apiClient.put<UpdateCaseResponse>(`${this.endpoint}/caso-code/${caseCode}`, updateData)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al actualizar el caso ${caseCode}`)
    }
  }

  // ============================================================================
  // FUNCIONES DE ASIGNACIÓN DE PATÓLOGOS
  // ============================================================================

  /**
   * Asigna un patólogo a un caso
   * @param caseCode - Código del caso
   * @param pathologistData - Datos del patólogo
   * @returns Caso con patólogo asignado
   */
  async assignPathologist(caseCode: string, pathologistData: { codigo: string; nombre: string }): Promise<CaseModel> {
    try {
      const response = await apiClient.put<CaseModel>(`${this.endpoint}/caso-code/${caseCode}/asignar-patologo`, pathologistData)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al asignar patólogo al caso ${caseCode}`)
    }
  }

  /**
   * Desasigna un patólogo de un caso
   * @param caseCode - Código del caso
   * @returns Caso sin patólogo asignado
   */
  async unassignPathologist(caseCode: string): Promise<CaseModel> {
    try {
      const response = await apiClient.delete<CaseModel>(`${this.endpoint}/caso-code/${caseCode}/desasignar-patologo`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al desasignar patólogo del caso ${caseCode}`)
    }
  }

  // ============================================================================
  // FUNCIONES DE ELIMINACIÓN
  // ============================================================================

  /**
   * Elimina un caso permanentemente
   * @param caseCode - Código del caso
   * @returns Confirmación de eliminación
   */
  async deleteCase(caseCode: string): Promise<DeleteCaseResponse> {
    try {
      const response = await apiClient.delete<DeleteCaseResponse>(`${this.endpoint}/caso-code/${caseCode}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al eliminar el caso ${caseCode}`)
    }
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Maneja errores de validación de la API
   * @param error - Error capturado
   * @returns Error formateado
   */
  private handleValidationError(error: any): Error {
    if (error.response?.data?.detail) {
      const validationErrors = Array.isArray(error.response.data.detail) 
        ? error.response.data.detail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`).join(', ')
        : error.response.data.detail
      return new Error(`Error de validación: ${validationErrors}`)
    }
    
    if (error.response?.data?.message) {
      return new Error(error.response.data.message)
    }
    
    return new Error(error.message || 'Error al crear el caso médico')
  }
}

// Exportar instancia singleton
export const casesApiService = new CasesApiService()
export default casesApiService
