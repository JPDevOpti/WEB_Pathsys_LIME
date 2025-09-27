import type { TestsReportData, TestDetails, EntitySelection } from '../types/tests.types'
import { buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class TestsApiService {
  private baseCases = `/cases`

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = buildApiUrl(endpoint)
    
    const defaultOptions: RequestInit = {
      headers: getAuthHeaders(),
      ...options,
    }

    try {
      const response = await fetch(url, defaultOptions)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`Error en API request a ${endpoint}:`, error)
      throw error
    }
  }

  async getMonthlyTests(month: number, year: number, entity?: string): Promise<TestsReportData> {
    try {
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${this.baseCases}/statistics/tests/monthly-performance?month=${month}&year=${year}${entityParam}`
      
      console.log('🔍 Tests API Debug:', {
        month,
        year,
        entity,
        entityParam,
        endpoint
      })
      
      const response = await this.makeRequest<any>(endpoint)
      
      console.log('📊 Tests API Response:', {
        testsCount: response.tests?.length || 0,
        summary: response.summary,
        firstTest: response.tests?.[0]
      })
      
      return {
        tests: response.tests || [],
        summary: response.summary || {
          totalSolicitadas: 0,
          totalCompletadas: 0,
          tiempoPromedio: 0
        }
      }
    } catch (error) {
      console.error('Error al obtener estadísticas mensuales:', error)
      throw error
    }
  }

  async getTestDetails(entity: string, codigoPrueba: string, month: number, year: number): Promise<TestDetails> {
    try {
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${this.baseCases}/statistics/tests/details/${codigoPrueba}?month=${month}&year=${year}${entityParam}`
      const response = await this.makeRequest<any>(endpoint)
      
      return response
    } catch (error) {
      console.error('Error al obtener detalles de la prueba:', error)
      throw error
    }
  }

  async getPathologists(entity: string, codigoPrueba: string, month: number, year: number): Promise<any[]> {
    try {
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${this.baseCases}/statistics/tests/pathologists/${codigoPrueba}?month=${month}&year=${year}${entityParam}`
      const response = await this.makeRequest<any>(endpoint)
      
      return response.pathologists || []
    } catch (error) {
      console.error('Error al obtener patólogos:', error)
      throw error
    }
  }

  async getEntities(): Promise<EntitySelection[]> {
    try {
      const endpoint = `/entities?limit=100`
      const response = await this.makeRequest<any>(endpoint)
      
      if (Array.isArray(response)) {
        return response.map((entidad: any) => ({
          codigo: entidad.id || '',
          nombre: entidad.name || ''
        }))
      } else {
        return []
      }
    } catch (error) {
      console.error('Error al obtener entidades:', error)
      return []
    }
  }

}

export const testsApiService = new TestsApiService()