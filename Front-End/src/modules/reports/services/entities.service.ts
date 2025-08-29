import type { EntityStats, EntitiesReportData, EntityDetails } from '../types/entities.types'
import { API_CONFIG, buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class EntitiesApiService {
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

  async getMonthlyEntities(month: number, year: number, entity?: string): Promise<EntitiesReportData> {
    try {
      let endpoint = `${API_CONFIG.ENDPOINTS.CASOS.ESTADISTICAS_ENTIDADES}?month=${month}&year=${year}`
      
      // Si se especifica una entidad, agregar el filtro
      if (entity && entity.trim()) {
        endpoint += `&entity=${encodeURIComponent(entity.trim())}`
      }
      
      const response = await this.makeRequest<any>(endpoint)
      
      if (response.entities) {
        // Transformar la respuesta del backend al formato esperado por el frontend
        const entities: EntityStats[] = response.entities.map((entity: any) => ({
          nombre: entity.nombre || '',
          codigo: entity.codigo || '',
          ambulatorios: entity.ambulatorios || 0,
          hospitalizados: entity.hospitalizados || 0,
          total: entity.total || 0
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
      } else {
        throw new Error('Formato de respuesta inválido del servidor')
      }
    } catch (error) {
      console.error('Error al obtener estadísticas de entidades:', error)
      throw error
    }
  }

  async getEntityDetails(entityCode: string, period: string): Promise<EntityDetails> {
    try {
      const endpoint = `${API_CONFIG.ENDPOINTS.CASOS.DETALLE_ENTIDAD}?entidad=${encodeURIComponent(entityCode)}&month=${period.split('-')[1]}&year=${period.split('-')[0]}`
      const response = await this.makeRequest<any>(endpoint)
      
      if (!response.detalles) {
        throw new Error('Formato de respuesta inválido del servidor')
      }
      
      const detalles = response.detalles
      
      // Transformar los datos al formato esperado
      const result: EntityDetails = {
        estadisticas_basicas: {
          total_pacientes: detalles.total_casos || 0,
          ambulatorios: detalles.ambulatorios || 0,
          hospitalizados: detalles.hospitalizados || 0,
          promedio_muestras_por_paciente: detalles.promedio_muestras_por_paciente || 0
        },
        tiempos_procesamiento: {
          promedio_dias: detalles.tiempo_promedio || 0,
          minimo_dias: detalles.tiempo_minimo || 0,
          maximo_dias: detalles.tiempo_maximo || 0,
          muestras_completadas: detalles.casos_completados || 0
        },
        pruebas_mas_solicitadas: detalles.pruebas_mas_solicitadas || []
      }
      
      return result
    } catch (error) {
      throw new Error(`Error al obtener detalles de la entidad: ${error}`)
    }
  }

  async getEntityPathologists(entityCode: string, period: string): Promise<any[]> {
    try {
      const endpoint = `${API_CONFIG.ENDPOINTS.CASOS.PATOLOGOS_POR_ENTIDAD}?entidad=${encodeURIComponent(entityCode)}&month=${period.split('-')[1]}&year=${period.split('-')[0]}`
      const response = await this.makeRequest<any>(endpoint)
      
      if (!response.patologos) {
        return []
      }
      
      const result: any[] = (response.patologos || []).map((pat: any) => ({
        codigo: pat.codigo || pat.patologo_code || '',
        nombre: pat.nombre || pat.patologo_name || 'Sin nombre',
        totalCasos: pat.total_casos || 0,
        casosCompletados: pat.casos_completados || 0,
        tiempoPromedio: pat.tiempo_promedio || 0,
        casosPorMes: pat.casos_por_mes || []
      }))
      
      return result
    } catch (error) {
      throw new Error(`Error al obtener patólogos de la entidad: ${error}`)
    }
  }

  // Método para verificar la conectividad con el backend
  async checkBackendConnection(): Promise<boolean> {
    try {
      const response = await this.makeRequest<any>(API_CONFIG.ENDPOINTS.CASOS.TEST)
      return response.message === 'Casos router funcionando correctamente'
    } catch (error) {
      console.error('Error de conectividad con el backend:', error)
      return false
    }
  }
}

export const entitiesApiService = new EntitiesApiService()
