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
        console.warn(`API request fallida (${endpoint}). Causa:`, error)
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
        console.warn('Error al obtener estadísticas mensuales:', error)
      throw error
    }
  }

  async getTestDetails(entity: string, codigoPrueba: string, month: number, year: number): Promise<TestDetails> {
    try {
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${this.baseCases}/statistics/tests/details/${codigoPrueba}?month=${month}&year=${year}${entityParam}`
      const response = await this.makeRequest<any>(endpoint)

      // Sanitizar posibles nulls en tiempo_promedio (si el backend empezara a permitirlos)
      if (response?.patologos && Array.isArray(response.patologos)) {
        response.patologos = response.patologos.map((p: any) => ({
          ...p,
          tiempo_promedio: typeof p?.tiempo_promedio === 'number' ? p.tiempo_promedio : 0
        }))
      }
      return response
    } catch (error: any) {
        console.warn('Error al obtener detalles de la prueba:', error)
      // Fallback: si falla por validación (p. ej., tiempo_promedio = null), intentar cargar al menos los patólogos
      try {
        const pathologists = await this.getPathologists(entity, codigoPrueba, month, year)
        const sanitized = (Array.isArray(pathologists) ? pathologists : []).map((p: any) => ({
          nombre: p?.nombre || 'N/A',
          codigo: p?.codigo || '',
          total_procesadas: Number(p?.total_procesadas) || 0,
          tiempo_promedio: typeof p?.tiempo_promedio === 'number' ? p.tiempo_promedio : 0
        }))

        const totalCasos = sanitized.reduce((acc: number, cur: any) => acc + (Number(cur.total_procesadas) || 0), 0)
        const fallback: TestDetails = {
          estadisticas_principales: {
            total_solicitadas: 0,
            total_completadas: 0,
            porcentaje_completado: 0
          },
          tiempos_procesamiento: {
            promedio_dias: 0,
            dentro_oportunidad: 0,
            fuera_oportunidad: 0,
            total_casos: totalCasos
          },
          patologos: sanitized
        }
          console.info('Usando datos de patólogos como fallback para detalles de prueba.')
        return fallback
      } catch (fallbackError) {
          console.warn('Fallback de patólogos también falló:', fallbackError)
        // Secondary fallback: derive details from monthly tests stats to avoid zeroed UI
        try {
          const monthly = await this.getMonthlyTests(month, year, entity && entity !== '' && entity !== 'general' ? entity : undefined)
          const match = Array.isArray(monthly.tests) ? monthly.tests.find((t: any) => t?.codigo === codigoPrueba) : null
          if (match) {
            const solicitadas = Number(match?.solicitadas) || 0
            const completadas = Number(match?.completadas) || 0
            const promedio = typeof match?.tiempoPromedio === 'number' && !Number.isNaN(match.tiempoPromedio) ? match.tiempoPromedio : 0
            const fromStats: TestDetails = {
              estadisticas_principales: {
                total_solicitadas: solicitadas,
                total_completadas: completadas,
                porcentaje_completado: solicitadas > 0 ? Math.round((completadas / solicitadas) * 100) : 0
              },
              tiempos_procesamiento: {
                promedio_dias: promedio,
                dentro_oportunidad: 0,
                fuera_oportunidad: 0,
                total_casos: completadas
              },
              patologos: []
            }
            // Enrich within/out-of-opportunity using monthly opportunity endpoint (best-effort)
            try {
              const oppEntityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
              const oppEndpoint = `${this.baseCases}/statistics/opportunity/monthly?month=${month}&year=${year}${oppEntityParam}`
              const oppResp = await this.makeRequest<any>(oppEndpoint)
              const oppTests = Array.isArray(oppResp?.tests) ? oppResp.tests : []
              const oppMatch = oppTests.find((t: any) => String(t.code || '') === codigoPrueba || String(t.codigo || '') === codigoPrueba)
              if (oppMatch) {
                const within = Number(oppMatch.withinOpportunity ?? oppMatch.dentroOportunidad) || 0
                const out = Number(oppMatch.outOfOpportunity ?? oppMatch.fueraOportunidad) || 0
                fromStats.tiempos_procesamiento.dentro_oportunidad = within
                fromStats.tiempos_procesamiento.fuera_oportunidad = out
                const sum = within + out
                if (sum > 0) {
                  fromStats.tiempos_procesamiento.total_casos = sum
                }
              }
            } catch (e) {
              console.warn('Opportunity fallback enrichment failed:', e)
            }
            // Enrich pathologists list using monthly performance endpoint (best-effort)
            try {
              const patoEndpoint = `${this.baseCases}/statistics/pathologists/monthly-performance?month=${month}&year=${year}`
              const patoResp = await this.makeRequest<any>(patoEndpoint)
              const patoBlocks = Array.isArray(patoResp?.pathologists) ? patoResp.pathologists : []
              fromStats.patologos = patoBlocks.map((p: any) => ({
                nombre: String(p.name || ''),
                codigo: String(p.code || ''),
                total_procesadas: Number(p.withinOpportunity || 0) + Number(p.outOfOpportunity || 0),
                tiempo_promedio: Number(p.averageDays || 0)
              }))
            } catch (pe) {
              console.warn('Monthly pathologists fallback enrichment failed:', pe)
            }
              console.info('Using monthly tests summary as fallback for test details.')
            return fromStats
          }
        } catch (statsFallbackError) {
            console.warn('Fallback desde estadísticas mensuales también falló:', statsFallbackError)
        }
        // Final fallback: minimal empty object to keep UI stable
        const empty: TestDetails = {
          estadisticas_principales: {
            total_solicitadas: 0,
            total_completadas: 0,
            porcentaje_completado: 0
          },
          tiempos_procesamiento: {
            promedio_dias: 0,
            dentro_oportunidad: 0,
            fuera_oportunidad: 0,
            total_casos: 0
          },
          patologos: []
        }
          console.info('Retornando datos vacíos para detalles de prueba por error de validación del backend.')
        return empty
      }
    }
  }

  async getPathologists(entity: string, codigoPrueba: string, month: number, year: number): Promise<any[]> {
    try {
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${this.baseCases}/statistics/tests/pathologists/${codigoPrueba}?month=${month}&year=${year}${entityParam}`
      const response = await this.makeRequest<any>(endpoint)
      
      return response.pathologists || []
    } catch (error) {
        console.warn('Error al obtener patólogos:', error)
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
        console.warn('Error al obtener entidades:', error)
      return []
    }
  }

}

export const testsApiService = new TestsApiService()