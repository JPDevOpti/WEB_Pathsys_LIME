import type { EntityStats, EntitiesReportData, EntityDetails } from '../types/entities.types'
import { buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class EntitiesApiService {
  private baseCases = `/cases`

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = buildApiUrl(endpoint)
    
    const defaultOptions: RequestInit = {
      headers: getAuthHeaders(),
      ...options,
    }

    const response = await fetch(url, defaultOptions)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Error HTTP ${response.status}`)
    }
    return await response.json()
  }

  async getMonthlyEntities(month: number, year: number, entity?: string): Promise<EntitiesReportData> {
    let endpoint = `${this.baseCases}/statistics/entities/monthly-performance?month=${month}&year=${year}`
    if (entity && entity.trim()) {
      endpoint += `&entity=${encodeURIComponent(entity.trim())}`
    }

    const response = await this.makeRequest<any>(endpoint)
    if (!response.entities) {
      throw new Error('Respuesta inválida del servidor')
    }

    const entities: EntityStats[] = response.entities.map((item: any) => ({
      nombre: item.nombre || '',
      codigo: item.codigo || '',
      ambulatorios: item.ambulatorios || 0,
      hospitalizados: item.hospitalizados || 0,
      total: item.total || 0
    }))

    return {
      entities,
      summary: response.summary || {
        total: 0,
        ambulatorios: 0,
        hospitalizados: 0,
        tiempoPromedio: 0
      }
    }
  }

  async getEntityDetails(entityCode: string, period: string): Promise<EntityDetails> {
    const [year, month] = period.split('-')
    const endpoint = `${this.baseCases}/statistics/entities/details?entidad=${encodeURIComponent(entityCode)}&month=${month}&year=${year}`
    const response = await this.makeRequest<any>(endpoint)

    if (!response.detalles) {
      throw new Error('Respuesta inválida del servidor')
    }

    const detalles = response.detalles
    const result: EntityDetails = {
      estadisticas_basicas: {
        total_pacientes: detalles.estadisticas_basicas?.total_pacientes || 0,
        ambulatorios: detalles.estadisticas_basicas?.ambulatorios || 0,
        hospitalizados: detalles.estadisticas_basicas?.hospitalizados || 0,
        promedio_muestras_por_paciente: detalles.estadisticas_basicas?.promedio_muestras_por_paciente || 0
      },
      tiempos_procesamiento: {
        promedio_dias: detalles.tiempos_procesamiento?.promedio_dias || 0,
        minimo_dias: detalles.tiempos_procesamiento?.minimo_dias || 0,
        maximo_dias: detalles.tiempos_procesamiento?.maximo_dias || 0,
        muestras_completadas: detalles.tiempos_procesamiento?.muestras_completadas || 0
      },
      pruebas_mas_solicitadas: detalles.pruebas_mas_solicitadas || []
    }

    return result
  }

  async getEntityPathologists(entityCode: string, period: string): Promise<any[]> {
    const [year, month] = period.split('-')
    const endpoint = `${this.baseCases}/statistics/entities/pathologists?entidad=${encodeURIComponent(entityCode)}&month=${month}&year=${year}`
    const response = await this.makeRequest<any>(endpoint)

    if (!response.patologos) {
      return []
    }

    return response.patologos.map((pat: any) => ({
      codigo: pat.codigo || '',
      nombre: pat.nombre || 'Sin nombre',
      totalCasos: pat.total_casos || 0,
      casosCompletados: pat.casos_completados || 0,
      tiempoPromedio: pat.tiempo_promedio || 0
    }))
  }

}

export const entitiesApiService = new EntitiesApiService()
