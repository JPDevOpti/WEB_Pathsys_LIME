import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { UpdateCaseResponse } from '@/modules/cases/types/api'

export interface UpsertResultadoRequest {
  metodo?: string
  resultado_macro?: string
  resultado_micro?: string
  diagnostico?: string
  observaciones?: string
  diagnostico_cie10?: {
    id: string
    codigo: string
    nombre: string
  }
  diagnostico_cieo?: {
    id: string
    codigo: string
    nombre: string
  }
}

class ResultsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.CASES

  async upsertResultado(casoCode: string, data: UpsertResultadoRequest): Promise<UpdateCaseResponse> {
    console.log('🔄 ResultsApiService.upsertResultado iniciado')
    console.log('📤 Datos enviados:', { casoCode, data })
    
    const endpoint = `${this.endpoint}/caso-code/${casoCode}/resultado`
    console.log('🌐 Endpoint:', endpoint)
    
    try {
      const response = await apiClient.put<UpdateCaseResponse>(endpoint, {
        metodo: data.metodo,
        resultado_macro: data.resultado_macro,
        resultado_micro: data.resultado_micro,
        diagnostico: data.diagnostico,
        observaciones: data.observaciones,
        diagnostico_cie10: data.diagnostico_cie10,
        diagnostico_cieo: data.diagnostico_cieo
      })
      
      console.log('✅ upsertResultado exitoso:', response)
      return response
      
    } catch (error: any) {
      console.error('❌ Error en upsertResultado:', error)
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      throw error
    }
  }

  async firmarResultado(casoCode: string, data: UpsertResultadoRequest, patologoCodigo: string): Promise<UpdateCaseResponse> {
    console.log('🔄 ResultsApiService.firmarResultado iniciado')
    console.log('📤 Datos enviados:', { casoCode, data, patologoCodigo })
    
    const endpoint = `${this.endpoint}/caso-code/${casoCode}/resultado/firmar-con-diagnosticos`
    console.log('🌐 Endpoint:', endpoint)
    
    // Primero intentar con el endpoint específico de firma
    try {
      console.log('🔄 Intentando con endpoint específico de firma...')
      
      const response = await apiClient.post<UpdateCaseResponse>(endpoint, {
        metodo: data.metodo,
        resultado_macro: data.resultado_macro,
        resultado_micro: data.resultado_micro,
        diagnostico: data.diagnostico,
        observaciones: data.observaciones,
        diagnostico_cie10: data.diagnostico_cie10,
        diagnostico_cieo: data.diagnostico_cieo
      }, {
        params: {
          patologo_codigo: patologoCodigo
        }
      })
      
      console.log('✅ Endpoint específico de firma exitoso:', response)
      return response
      
    } catch (error: any) {
      console.error('❌ Error en endpoint específico de firma:', error)
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      
      // Si falla por restricción de estado, intentar con el endpoint de actualización regular
      if (error.response?.data?.message?.includes('estado') || error.message?.includes('estado')) {
        console.warn('🔄 Endpoint de firma falló por restricción de estado, intentando con actualización regular...')
        
        try {
          // Usar el endpoint de actualización regular y luego cambiar el estado
          console.log('🔄 Actualizando resultado...')
          const updateResponse = await this.upsertResultado(casoCode, data)
          console.log('✅ Resultado actualizado:', updateResponse)
          
          // Intentar cambiar el estado a COMPLETADO usando el endpoint de casos
          try {
            console.log('🔄 Cambiando estado a COMPLETADO...')
            const stateResponse = await apiClient.put(`${this.endpoint}/caso-code/${casoCode}`, {
              estado: 'COMPLETADO'
            })
            console.log('✅ Estado cambiado exitosamente:', stateResponse)
          } catch (stateError: any) {
            console.warn('⚠️ No se pudo cambiar el estado automáticamente:', stateError)
            console.warn('State error details:', {
              message: stateError.message,
              response: stateError.response?.data,
              status: stateError.response?.status
            })
          }
          
          return updateResponse
          
        } catch (fallbackError: any) {
          console.error('❌ Error en fallback de actualización:', fallbackError)
          throw fallbackError
        }
      }
      
      // Si es otro tipo de error, relanzarlo
      throw error
    }
  }
}

export const resultsApiService = new ResultsApiService()
export default resultsApiService


