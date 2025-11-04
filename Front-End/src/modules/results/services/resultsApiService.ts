import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { UpdateCaseResponse } from '@/modules/cases/types/api'

// Nueva interfaz para el nuevo backend
export interface UpdateResultRequest {
  method?: string[]
  macro_result?: string
  micro_result?: string
  diagnosis?: string
  observations?: string
  cie10_diagnosis?: {
    id?: string
    code: string
    name: string
  }
  cieo_diagnosis?: {
    id?: string
    code: string
    name: string
  }
  diagnostico_cie10?: {
    id?: string
    codigo: string
    nombre: string
  }
  diagnostico_cieo?: {
    id?: string
    codigo: string
    nombre: string
  }
}

// Interfaz legacy para compatibilidad con el backend actual
export interface UpsertResultadoRequest {
  metodo?: string[]
  resultado_macro?: string
  resultado_micro?: string
  diagnostico?: string
  observaciones?: string
  diagnostico_cie10?: {
    id?: string
    codigo: string
    nombre: string
  }
  diagnostico_cieo?: {
    id?: string
    codigo: string
    nombre: string
  }
}

class ResultsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES
  private readonly newBackendEndpoint = '/cases' // Nuevo endpoint del backend

  // Nuevo método para el nuevo backend
  async updateCaseResult(caseCode: string, data: UpdateResultRequest): Promise<any> {
    try {
      const endpoint = `${this.newBackendEndpoint}/${caseCode}/result`
      const response = await apiClient.put(endpoint, data)
      return response
    } catch (error: any) {
      throw new Error(`Error al actualizar resultado: ${error.message || error}`)
    }
  }

  // Nuevo método para obtener resultado
  async getCaseResult(caseCode: string): Promise<any> {
    try {
      const endpoint = `${this.newBackendEndpoint}/${caseCode}/result`
      const response = await apiClient.get(endpoint)
      return response
    } catch (error: any) {
      throw new Error(`Error al obtener resultado: ${error.message || error}`)
    }
  }

  // Nuevo método para validar si se puede editar
  async validateCaseForEditing(caseCode: string): Promise<any> {
    try {
      const endpoint = `${this.newBackendEndpoint}/${caseCode}/result/validation`
      const response = await apiClient.get(endpoint)
      return response
    } catch (error: any) {
      throw new Error(`Error al validar caso: ${error.message || error}`)
    }
  }

  // Método legacy para compatibilidad
  async upsertResultado(casoCode: string, data: UpsertResultadoRequest): Promise<UpdateCaseResponse> {
    try {
      const endpoint = `${this.endpoint}/caso-code/${casoCode}/resultado`
      const response = await apiClient.put<UpdateCaseResponse>(endpoint, {
        metodo: data.metodo,
        resultado_macro: data.resultado_macro,
        resultado_micro: data.resultado_micro,
        diagnostico: data.diagnostico,
        observaciones: data.observaciones,
        diagnostico_cie10: data.diagnostico_cie10,
        diagnostico_cieo: data.diagnostico_cieo
      })
      return response
    } catch (error: any) {
      throw new Error(`Error al actualizar resultado: ${error}`)
    }
  }

  async firmarResultado(casoCode: string, data: UpsertResultadoRequest, patologoCodigo: string): Promise<UpdateCaseResponse> {
    try {
      const endpoint = `${this.endpoint}/caso-code/${casoCode}/resultado/firmar-con-diagnosticos`
      const payload = {
        metodo: data.metodo,
        resultado_macro: data.resultado_macro,
        resultado_micro: data.resultado_micro,
        diagnostico: data.diagnostico,
        observaciones: data.observaciones,
        diagnostico_cie10: data.diagnostico_cie10,
        diagnostico_cieo: data.diagnostico_cieo
      }
      
      try {
        const response = await apiClient.post<UpdateCaseResponse>(endpoint, payload, {
          params: {
            patologo_codigo: patologoCodigo
          }
        })
        return response
      } catch (error: any) {
        if (error.response?.status === 404) {
          const alternativeEndpoint = `${this.endpoint}/caso-code/${casoCode}/resultado/firmar`
          const response = await apiClient.post<UpdateCaseResponse>(alternativeEndpoint, payload, {
            params: {
              patologo_codigo: patologoCodigo
            }
          })
          return response
        }
        throw error
      }
    } catch (error) {
      throw new Error(`Error al firmar resultado: ${error}`)
    }
  }

  async cambiarEstadoResultado(casoCode: string, nuevoEstado: string): Promise<any> {
    try {
      const endpoint = `${this.endpoint}/caso-code/${casoCode}`
      const response = await apiClient.put(endpoint, {
        estado: nuevoEstado
      })
      return response.data
    } catch (error) {
      throw new Error(`Error al cambiar estado del resultado: ${error}`)
    }
  }
}

export const resultsApiService = new ResultsApiService()
export default resultsApiService


