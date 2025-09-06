import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  CaseModel, CaseListResponse, CaseSearchResponse, CaseStatisticsResponse,
  CreateCaseRequest, CreateCaseResponse, UpdateCaseRequest, UpdateCaseResponse,
  DeleteCaseResponse, CaseSearchParams, CaseListParams
} from '../types'

export class CasesApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES

  /**
   * Limpia campos duplicados de estado activo que puede agregar el backend
   * Mantiene snake_case (is_active) y elimina camelCase (isActive)
   */
  private cleanDuplicateActiveFields(data: any): any {
    if (!data || typeof data !== 'object') return data
    
    // Si es un array, limpiar cada elemento
    if (Array.isArray(data)) {
      return data.map(item => this.cleanDuplicateActiveFields(item))
    }
    
    // Si ambos campos existen, eliminar el camelCase
    if ('isActive' in data && 'is_active' in data) {
      const cleaned = { ...data }
      delete cleaned.isActive
      return cleaned
    }
    
    return data
  }

  async consultarConsecutivo(): Promise<{ codigo_consecutivo: string; mensaje: string }> {
    try {
      const response = await apiClient.get<{ codigo_consecutivo: string; mensaje: string }>(`${this.endpoint}/siguiente-consecutivo`)
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al consultar el consecutivo')
    }
  }

  async getCases(params: CaseListParams = {}): Promise<CaseListResponse> {
    try {
      const response = await apiClient.get<CaseListResponse>(this.endpoint, { params })
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener la lista de casos')
    }
  }

  async getCaseByCode(caseCode: string): Promise<CaseModel> {
    try {
      const response = await apiClient.get<CaseModel>(`${this.endpoint}/caso-code/${caseCode}`)
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener el caso ${caseCode}`)
    }
  }

  async getCasesByPatient(cedula: string): Promise<CaseModel[]> {
    try {
      const response = await apiClient.get<CaseModel[]>(`${this.endpoint}/paciente/${cedula}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener casos del paciente ${cedula}`)
    }
  }

  async getCasesByPathologist(codigo: string): Promise<CaseListResponse> {
    try {
      const response = await apiClient.get<CaseListResponse>(`${this.endpoint}/patologo/${codigo}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener casos del patólogo ${codigo}`)
    }
  }

  async getCasesByState(estado: string): Promise<CaseListResponse> {
    try {
      const response = await apiClient.get<CaseListResponse>(`${this.endpoint}/estado/${estado}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener casos con estado ${estado}`)
    }
  }

  async getCaseStatistics(): Promise<CaseStatisticsResponse> {
    try {
      const response = await apiClient.get<CaseStatisticsResponse>(`${this.endpoint}/estadisticas`)
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener estadísticas del sistema')
    }
  }

  async searchCases(searchParams: CaseSearchParams): Promise<CaseSearchResponse> {
    try {
      const response = await apiClient.post<CaseSearchResponse>(`${this.endpoint}/buscar`, searchParams)
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al buscar casos')
    }
  }

  async searchCasesAdvanced(searchParams: CaseSearchParams): Promise<CaseSearchResponse> {
    try {
      const response = await apiClient.get<CaseSearchResponse>(`${this.endpoint}/search`, { params: searchParams })
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error en la búsqueda avanzada')
    }
  }

  async createCase(caseData: CreateCaseRequest): Promise<CreateCaseResponse> {
    try {
      const response = await apiClient.post<CreateCaseResponse>(this.endpoint, caseData)
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
      throw this.handleValidationError(error)
    }
  }

  async updateCase(caseCode: string, updateData: UpdateCaseRequest): Promise<UpdateCaseResponse> {
    try {
      const response = await apiClient.put<UpdateCaseResponse>(`${this.endpoint}/caso-code/${caseCode}`, updateData)
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
  // Reutilizar formateo de errores de validación
  throw this.handleValidationError(error)
    }
  }

  async assignPathologist(caseCode: string, pathologistData: { codigo: string; nombre: string }): Promise<CaseModel> {
    try {
      const response = await apiClient.put<CaseModel>(`${this.endpoint}/caso-code/${caseCode}/asignar-patologo`, pathologistData)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al asignar patólogo al caso ${caseCode}`)
    }
  }

  async unassignPathologist(caseCode: string): Promise<CaseModel> {
    try {
      const response = await apiClient.delete<CaseModel>(`${this.endpoint}/caso-code/${caseCode}/desasignar-patologo`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al desasignar patólogo del caso ${caseCode}`)
    }
  }

  async deleteCase(caseCode: string): Promise<DeleteCaseResponse> {
    try {
      const response = await apiClient.delete<DeleteCaseResponse>(`${this.endpoint}/caso-code/${caseCode}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al eliminar el caso ${caseCode}`)
    }
  }

  /**
   * Marca múltiples casos como Completado aplicando cambios en sus muestras.
   * Genera múltiples peticiones secuenciales al endpoint updateCase existente.
   * pendingCases: array de objetos con { caseCode, remainingSubsamples, oportunidad, entregadoA, fechaEntrega } donde remainingSubsamples es el arreglo final que debe persistir.
   */
  async batchCompleteCases(pendingCases: Array<{ 
    caseCode: string; 
    remainingSubsamples: Array<{ region_cuerpo: string; pruebas: Array<{ id: string; nombre?: string; cantidad: number }> }>; 
    oportunidad?: number;
    entregadoA?: string;
    fechaEntrega?: string;
  }>): Promise<any[]> {
    const results: any[] = []
    for (const item of pendingCases) {
      try {
        const payload: any = {
          estado: 'Completado',
          muestras: item.remainingSubsamples
        }
        
        // Incluir campo oportunidad si está presente
        if (item.oportunidad !== undefined) {
          payload.oportunidad = item.oportunidad
        }
        
        // Incluir campos de entrega si están presentes
        if (item.entregadoA) {
          payload.entregado_a = item.entregadoA
        }
        
        if (item.fechaEntrega) {
          payload.fecha_entrega = item.fechaEntrega
        }
        const updated = await this.updateCase(item.caseCode, payload)
        results.push({ caseCode: item.caseCode, success: true, data: updated })
      } catch (err: any) {
        results.push({ caseCode: item.caseCode, success: false, error: err.message || String(err) })
      }
    }
    return results
  }

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

export const casesApiService = new CasesApiService()
export default casesApiService
