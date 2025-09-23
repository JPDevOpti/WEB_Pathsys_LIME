import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  CaseModel, CaseListResponse, CaseSearchResponse, CaseStatisticsResponse,
  CreateCaseResponse, UpdateCaseResponse,
  DeleteCaseResponse, CaseSearchParams, CaseListParams
} from '../types'

export class CasesApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES

  // Normalize responses by removing duplicate active flags recursively
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

  // Small helpers to reduce boilerplate in requests
  private async getClean<T>(url: string, config?: any): Promise<T> {
    try { return this.cleanDuplicateActiveFields(await apiClient.get<T>(url, config)) } 
    catch (error: any) { throw new Error(error.message || `Error GET ${url}`) }
  }
  private async postClean<T>(url: string, body?: any, config?: any): Promise<T> {
    try { return this.cleanDuplicateActiveFields(await apiClient.post<T>(url, body, config)) } 
    catch (error: any) { throw new Error(error.message || `Error POST ${url}`) }
  }
  private async putClean<T>(url: string, body?: any, config?: any): Promise<T> {
    try { return this.cleanDuplicateActiveFields(await apiClient.put<T>(url, body, config)) } 
    catch (error: any) { throw this.handleValidationError(error) }
  }
  private async deleteRaw<T>(url: string, config?: any): Promise<T> {
    try { return await apiClient.delete<T>(url, config) } 
    catch (error: any) { throw new Error(error.message || `Error DELETE ${url}`) }
  }

  async consultarConsecutivo(): Promise<{ codigo_consecutivo: string; mensaje: string }> {
    return this.getClean<{ codigo_consecutivo: string; mensaje: string }>(`${this.endpoint}/siguiente-consecutivo`)
  }

  async getCases(params: CaseListParams = {}): Promise<CaseListResponse> {
    return this.getClean<CaseListResponse>(this.endpoint, { params })
  }

  async getCaseByCode(caseCode: string): Promise<CaseModel> {
    return this.getClean<CaseModel>(`${this.endpoint}/${encodeURIComponent(caseCode)}`)
  }

  async getCasesByPatient(cedula: string): Promise<CaseModel[]> {
    return this.getClean<CaseModel[]>(`${this.endpoint}/?search=${cedula}&limit=1000`)
  }

  async getCasesByPathologist(codigo: string): Promise<CaseListResponse> {
    return this.getClean<CaseListResponse>(`${this.endpoint}/patologo/${codigo}`)
  }

  async getCasesByState(estado: string): Promise<CaseListResponse> {
    return this.getClean<CaseListResponse>(`${this.endpoint}/estado/${estado}`)
  }

  async getCaseStatistics(): Promise<CaseStatisticsResponse> {
    return this.getClean<CaseStatisticsResponse>(`${this.endpoint}/estadisticas`)
  }

  async searchCases(searchParams: CaseSearchParams): Promise<CaseSearchResponse> {
    return this.postClean<CaseSearchResponse>(`${this.endpoint}/buscar`, searchParams)
  }

  async searchCasesAdvanced(searchParams: CaseSearchParams): Promise<CaseSearchResponse> {
    return this.getClean<CaseSearchResponse>(`${this.endpoint}/search`, { params: searchParams })
  }

  async createCase(caseData: any): Promise<any> {
    return this.postClean<CreateCaseResponse>(this.endpoint, caseData)
  }

  async updateCase(caseCode: string, updateData: any): Promise<any> {
    return this.putClean<UpdateCaseResponse>(`${this.endpoint}/${caseCode}`, updateData)
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
    return this.deleteRaw<DeleteCaseResponse>(`${this.endpoint}/${caseCode}`)
  }

  async addAdditionalNote(caseCode: string, note: string): Promise<UpdateCaseResponse> {
    try {
      // Usar el nuevo endpoint de actualización para agregar nota
      const updateData: any = {
        additional_notes: [{
          date: new Date().toISOString(),
          note: note
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
    remainingSubsamples: Array<{ body_region: string; tests: Array<{ id: string; name?: string; quantity: number }> }>; 
    business_days?: number;
    delivered_to?: string;
    delivered_at?: string;
  }>): Promise<any[]> {
    const results: any[] = []
    for (const item of pendingCases) {
      try {
        const updateData: any = {
          state: 'Completado',
          samples: item.remainingSubsamples,
          business_days: item.business_days,
          delivered_to: item.delivered_to,
          delivered_at: item.delivered_at ? new Date(item.delivered_at) : undefined
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
