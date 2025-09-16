import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestDetails, TestSearchParams, TestListResponse } from '../types/test'

class TestsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS
  
  private transformTestData(prueba: any): TestDetails {
    return {
      id: prueba.id || prueba._id || '',
      pruebaCode: prueba.test_code || prueba.prueba_code,
      pruebasName: prueba.name || prueba.prueba_name,
      pruebasDescription: prueba.description || prueba.prueba_description || '',
      tiempo: (prueba.time ?? prueba.tiempo ?? 0),
      isActive: typeof prueba.is_active === 'boolean' ? prueba.is_active : true,
      fechaCreacion: prueba.created_at || prueba.fecha_creacion,
      fechaActualizacion: prueba.updated_at || prueba.fecha_actualizacion
    }
  }
  
  async getTests(params: TestSearchParams = {}): Promise<TestListResponse> {
    try {
      const searchParams = new URLSearchParams()
      
      if (params.query) searchParams.append('query', params.query)
      if (params.skip !== undefined) searchParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) searchParams.append('limit', params.limit.toString())
      
      const url = searchParams.toString() ? `${this.endpoint}?${searchParams.toString()}` : this.endpoint
      const response = await apiClient.get(url)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (Array.isArray(data)) {
        const pruebas = data.map((p: any) => this.transformTestData(p))
        return { pruebas, total: pruebas.length, skip: 0, limit: pruebas.length, has_next: false, has_prev: false }
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
      const response = await apiClient.get(`${this.endpoint}?limit=1000`)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (Array.isArray(data)) return data.map((p: any) => this.transformTestData(p)).filter(t => t.isActive)
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        return data.pruebas.map((prueba: any) => this.transformTestData(prueba)).filter((t: TestDetails) => t.isActive)
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) return data[key].map((p: any) => this.transformTestData(p)).filter((t: TestDetails) => t.isActive)
      }
      
      return []
      
    } catch (error: any) {
      throw new Error(`Error al obtener pruebas activas: ${error.message}`)
    }
  }

  async getAllTestsIncludingInactive(): Promise<TestDetails[]> {
    try {
      const response = await apiClient.get(`${this.endpoint}?limit=1000`)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (Array.isArray(data)) return data.map((p: any) => this.transformTestData(p))
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        return data.pruebas.map((prueba: any) => this.transformTestData(prueba))
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) return data[key].map((p: any) => this.transformTestData(p))
      }
      
      return []
      
    } catch (error: any) {
      throw new Error(`Error al obtener todas las pruebas: ${error.message}`)
    }
  }
  
  async getTestByCode(pruebaCode: string): Promise<TestDetails> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${encodeURIComponent(pruebaCode)}`)
      
      if (!response) throw new Error('Respuesta vacía del servidor')
      
      const data = response
      
      if (data && (data.test_code || data.name || data.prueba_code || data.prueba_name)) {
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
      const response = await apiClient.get(`${this.endpoint}?query=${encodeURIComponent(query)}&limit=${limit}`)
      
      if (!response) throw new Error('La respuesta del servidor está vacía')
      
      const data = response
      
      if (Array.isArray(data)) return data.map((p: any) => this.transformTestData(p)).filter(t => t.isActive)
      
      if (data.pruebas && Array.isArray(data.pruebas)) {
        return data.pruebas.map((prueba: any) => this.transformTestData(prueba)).filter((t: TestDetails) => t.isActive)
      }
      
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) return data[key].map((p: any) => this.transformTestData(p)).filter((t: TestDetails) => t.isActive)
      }
      
      return []
      
    } catch (error: any) {
      throw new Error(`Error al buscar pruebas: ${error.message}`)
    }
  }
}

export const testsApiService = new TestsApiService()
