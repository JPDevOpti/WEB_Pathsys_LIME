import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestDetails, TestSearchParams, TestListResponse } from '../types/test'

/**
 * Servicio para manejar operaciones con pruebas médicas
 */
class TestsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS
  
  /**
   * Obtener lista de pruebas con filtros y paginación
   */
  async getTests(params: TestSearchParams = {}): Promise<TestListResponse> {
    const searchParams = new URLSearchParams()
    
    if (params.query) searchParams.append('query', params.query)
    if (params.activo !== undefined) searchParams.append('activo', params.activo.toString())
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString())
    
    const response = await apiClient.get(`${this.endpoint}/?${searchParams.toString()}`)
    return response.data
  }
  
  /**
   * Obtener todas las pruebas activas (sin paginación)
   */
  async getAllActiveTests(): Promise<TestDetails[]> {
    try {
      const data: any = await apiClient.get(`${this.endpoint}/?activo=true&limit=1000`)
      // Si data.pruebas existe y es un array, devolverlo
      if (data && Array.isArray(data.pruebas)) {
        return data.pruebas
      }
      // Si data es un array directamente, devolverlo
      if (Array.isArray(data)) {
        return data
      }
      // Si no hay datos válidos, devolver array vacío
      return []
    } catch (error) {
      console.error('💥 Error detallado en getAllActiveTests:', error)
      return []
    }
  }
  
  /**
   * Obtener prueba por código
   */
  async getTestByCode(pruebaCode: string): Promise<TestDetails> {
    const data: any = await apiClient.get(`${this.endpoint}/${pruebaCode}/`)
    // Si el backend devuelve directamente el objeto
    if (data && (data.pruebaCode || data.pruebasName)) return data
    // Si viene envuelto
    return (data?.data as TestDetails) || data
  }
  
  /**
   * Buscar pruebas por término
   */
  async searchTests(query: string, limit: number = 50): Promise<TestDetails[]> {
    try {
      const data: any = await apiClient.get(`${this.endpoint}/?query=${encodeURIComponent(query)}&activo=true&limit=${limit}`)
      
      if (!data) {
        throw new Error('La respuesta del servidor está vacía')
      }
      
      if (Array.isArray(data)) {
        return data
      }
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        return data.pruebas
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) {
          return data[key]
        }
      }
      
      throw new Error(`Formato de respuesta inesperado en búsqueda: ${JSON.stringify(data)}`)
    } catch (error) {
      console.error('💥 Error detallado en searchTests:', error)
      throw error
    }
  }
}

export const testsApiService = new TestsApiService()
