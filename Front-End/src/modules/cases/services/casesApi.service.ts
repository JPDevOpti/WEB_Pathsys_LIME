import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  CaseModel, CaseListResponse, CaseSearchResponse, CaseStatisticsResponse,
  CreateCaseResponse, UpdateCaseResponse,
  DeleteCaseResponse, CaseSearchParams, CaseListParams
} from '../types'

export class CasesApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES

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
      const response = await apiClient.get<CaseModel>(`${this.endpoint}/${encodeURIComponent(caseCode)}`)
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener el caso ${caseCode}`)
    }
  }

  async getCasesByPatient(cedula: string): Promise<CaseModel[]> {
    try {
      const response = await apiClient.get<CaseModel[]>(`${this.endpoint}/?search=${cedula}&limit=1000`)
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

  async createCase(caseData: any): Promise<any> {
    try {
      const response = await apiClient.post<CreateCaseResponse>(this.endpoint, caseData)
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
      throw this.handleValidationError(error)
    }
  }

  async updateCase(caseCode: string, updateData: any): Promise<any> {
    try {
      const response = await apiClient.put<UpdateCaseResponse>(`${this.endpoint}/${caseCode}`, updateData)
      return this.cleanDuplicateActiveFields(response)
    } catch (error: any) {
      // Reutilizar formateo de errores de validación
      throw this.handleValidationError(error)
    }
  }

  async assignPathologist(caseCode: string, pathologistData: { codigo: string; nombre: string }): Promise<UpdateCaseResponse> {
    try {
      // Usar el nuevo endpoint de actualización para asignar patólogo
      const updateData: any = {
        assigned_pathologist: {
          id: pathologistData.codigo,
          name: pathologistData.nombre
        }
      }
      return await this.updateCase(caseCode, updateData)
    } catch (error: any) {
      throw new Error(error.message || `Error al asignar patólogo al caso ${caseCode}`)
    }
  }

  async unassignPathologist(caseCode: string): Promise<UpdateCaseResponse> {
    try {
      // Usar el nuevo endpoint de actualización para desasignar patólogo
      const updateData: any = { assigned_pathologist: null }
      return await this.updateCase(caseCode, updateData)
    } catch (error: any) {
      throw new Error(error.message || `Error al desasignar patólogo del caso ${caseCode}`)
    }
  }

  async deleteCase(caseCode: string): Promise<any> {
    try {
      const response = await apiClient.delete<DeleteCaseResponse>(`${this.endpoint}/${caseCode}`)
      return response
    } catch (error: any) {
      throw new Error(error.message || `Error al eliminar el caso ${caseCode}`)
    }
  }

  async addAdditionalNote(caseCode: string, note: string, addedBy?: string): Promise<UpdateCaseResponse> {
    try {
      // Usar el nuevo endpoint de actualización para agregar nota
      const updateData: any = {
        notas_adicionales: [{
          fecha: new Date().toISOString(),
          nota: note,
          agregado_por: addedBy || 'Usuario'
        }]
      }
      return await this.updateCase(caseCode, updateData)
    } catch (error: any) {
      throw new Error(error.message || `Error al agregar nota adicional al caso ${caseCode}`)
    }
  }

  async updateCaseState(caseCode: string, state: string): Promise<UpdateCaseResponse> {
    try {
      const updateData = { state }
      return await this.updateCase(caseCode, updateData)
    } catch (error: any) {
      throw new Error(error.message || `Error al actualizar estado del caso ${caseCode}`)
    }
  }

  /**
   * Marca múltiples casos como Completado aplicando cambios en sus muestras.
   * Usa el nuevo endpoint de actualización unificado.
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
        const updateData: any = {
          estado: 'Completado',
          muestras: item.remainingSubsamples,
          oportunidad: item.oportunidad,
          entregado_a: item.entregadoA,
          fecha_entrega: item.fechaEntrega ? new Date(item.fechaEntrega) : undefined
        }
        
        // Eliminar campos undefined para payload más limpio
        Object.keys(updateData).forEach(k => (updateData as any)[k] === undefined && delete (updateData as any)[k])
        
        const updated = await this.updateCase(item.caseCode, updateData)
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
