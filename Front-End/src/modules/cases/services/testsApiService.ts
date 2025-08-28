import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestDetails, TestSearchParams, TestListResponse } from '../types/test'

class TestsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS
  
  private transformTestData(prueba: any): TestDetails {
    return {
      id: prueba.id,
      pruebaCode: prueba.prueba_code,
      pruebasName: prueba.prueba_name,
      pruebasDescription: prueba.prueba_description || '',
      tiempo: prueba.tiempo || 0,
      isActive: prueba.is_active,
      fechaCreacion: prueba.fecha_creacion,
      fechaActualizacion: prueba.fecha_actualizacion
    }
  }
  
  async getTests(params: TestSearchParams = {}): Promise<TestListResponse> {
    try {
      const searchParams = new URLSearchParams()
      
      if (params.query) searchParams.append('query', params.query)
      if (params.activo !== undefined) searchParams.append('activo', params.activo.toString())
      if (params.skip !== undefined) searchParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) searchParams.append('limit', params.limit.toString())
      
      const response = await apiClient.get(`${this.endpoint}/?${searchParams.toString()}`)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (Array.isArray(data)) {
        return {
          pruebas: data,
          total: data.length,
          skip: 0,
          limit: data.length,
          has_next: false,
          has_prev: false
        }
      }
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        const transformedPruebas = data.pruebas.map((prueba: any) => this.transformTestData(prueba))
        
        return {
          pruebas: transformedPruebas,
          total: data.total || data.pruebas.length,
          skip: data.skip || 0,
          limit: data.limit || data.pruebas.length,
          has_next: data.has_next || false,
          has_prev: data.has_prev || false
        }
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) {
          return {
            pruebas: data[key],
            total: data[key].length,
            skip: 0,
            limit: data[key].length,
            has_next: false,
            has_prev: false
          }
        }
      }
      
      return {
        pruebas: [],
        total: 0,
        skip: 0,
        limit: 0,
        has_next: false,
        has_prev: false
      }
      
    } catch (error: any) {
      throw new Error(`Error al obtener pruebas: ${error.message}`)
    }
  }
  
  async getAllActiveTests(): Promise<TestDetails[]> {
    try {
      const response = await apiClient.get(`${this.endpoint}/?activo=true&limit=1000`)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (Array.isArray(data)) return data
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        return data.pruebas.map((prueba: any) => this.transformTestData(prueba))
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) return data[key]
      }
      
      return []
      
    } catch (error: any) {
      throw new Error(`Error al obtener pruebas activas: ${error.message}`)
    }
  }
  
  async getTestByCode(pruebaCode: string): Promise<TestDetails> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${pruebaCode}/`)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (data && (data.prueba_code || data.prueba_name)) {
        return this.transformTestData(data)
      }
      
      if (data.prueba && (data.prueba.prueba_code || data.prueba.prueba_name)) {
        return this.transformTestData(data.prueba)
      }
      
      throw new Error('Formato de respuesta inesperado para la prueba')
      
    } catch (error: any) {
      throw new Error(`Error al obtener prueba por código: ${error.message}`)
    }
  }
  
  async searchTests(query: string, limit: number = 50): Promise<TestDetails[]> {
    try {
      const response = await apiClient.get(`${this.endpoint}/?query=${encodeURIComponent(query)}&activo=true&limit=${limit}`)
      
      if (!response) throw new Error('La respuesta del servidor está vacía')
      
      const data = response
      
      if (Array.isArray(data)) return data
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        return data.pruebas.map((prueba: any) => this.transformTestData(prueba))
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) return data[key]
      }
      
      return []
      
    } catch (error: any) {
      throw new Error(`Error al buscar pruebas: ${error.message}`)
    }
  }
}

export const testsApiService = new TestsApiService()
