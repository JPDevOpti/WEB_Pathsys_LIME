import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestDetails, TestSearchParams, TestListResponse } from '../types/test'

class TestsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  // Normalize single test item
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

  // Parse response accepting arrays or various keyed arrays
  private parseTestListResponse(data: any): TestDetails[] {
    if (Array.isArray(data)) return data.map((p: any) => this.transformTestData(p))
    if (Array.isArray(data?.pruebas)) return data.pruebas.map((p: any) => this.transformTestData(p))
    for (const key of Object.keys(data || {})) {
      if (Array.isArray((data as any)[key])) return (data as any)[key].map((p: any) => this.transformTestData(p))
    }
    return []
  }

  private ensureEndpoint(): string { return this.endpoint.endsWith('/') ? this.endpoint : `${this.endpoint}/` }

  async getTests(params: TestSearchParams = {}): Promise<TestListResponse> {
    try {
      const searchParams = new URLSearchParams()
      if (params.query) searchParams.append('query', params.query)
      if (params.skip !== undefined) searchParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) searchParams.append('limit', params.limit.toString())
      const url = searchParams.toString() ? `${this.ensureEndpoint()}?${searchParams.toString()}` : this.ensureEndpoint()
      const data = await apiClient.get(url)
      const pruebas = this.parseTestListResponse(data)
      return {
        pruebas,
        total: (data?.total ?? pruebas.length) as number,
        skip: (data?.skip ?? 0) as number,
        limit: (data?.limit ?? pruebas.length) as number,
        has_next: Boolean(data?.has_next),
        has_prev: Boolean(data?.has_prev)
      }
    } catch (error: any) {
      throw new Error(`Error al obtener pruebas: ${error.message}`)
    }
  }

  async getAllActiveTests(): Promise<TestDetails[]> {
    try {
      const data = await apiClient.get(`${this.ensureEndpoint()}?limit=100`)
      return this.parseTestListResponse(data).filter(t => t.isActive)
    } catch (error: any) {
      throw new Error(`Error al obtener pruebas activas: ${error.message}`)
    }
  }

  async getAllTestsIncludingInactive(): Promise<TestDetails[]> {
    try {
      const data = await apiClient.get(`${this.endpoint}?limit=1000`)
      return this.parseTestListResponse(data)
    } catch (error: any) {
      throw new Error(`Error al obtener todas las pruebas: ${error.message}`)
    }
  }

  async getTestByCode(pruebaCode: string): Promise<TestDetails> {
    try {
      const data = await apiClient.get(`${this.endpoint}/${encodeURIComponent(pruebaCode)}`)
      if (data && (data.test_code || data.name || data.prueba_code || data.prueba_name)) return this.transformTestData(data)
      if (data?.prueba && (data.prueba.prueba_code || data.prueba.prueba_name)) return this.transformTestData(data.prueba)
      throw new Error('Formato de respuesta inesperado para la prueba')
    } catch (error: any) {
      throw new Error(`Error al obtener prueba por código: ${error.message}`)
    }
  }

  async searchTests(query: string, limit: number = 50): Promise<TestDetails[]> {
    try {
      const data = await apiClient.get(`${this.ensureEndpoint()}?query=${encodeURIComponent(query)}&limit=${limit}`)
      return this.parseTestListResponse(data).filter(t => t.isActive)
    } catch (error: any) {
      throw new Error(`Error al buscar pruebas: ${error.message}`)
    }
  }
}

export const testsApiService = new TestsApiService()
