import type { TestStats, TestsReportData, TestDetails, EntitySelection } from '../types/tests.types'
import { API_CONFIG, buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class TestsApiService {
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
      // Si la entidad está vacía o es 'general', no incluir el parámetro entity
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${API_CONFIG.ENDPOINTS.CASOS.ESTADISTICAS_PRUEBAS}?month=${month}&year=${year}${entityParam}`
      const response = await this.makeRequest<any>(endpoint)
      
      if (response.success && response.data) {
        // Transformar la respuesta del backend al formato esperado por el frontend
        const tests: TestStats[] = response.data.pruebas.map((prueba: any) => ({
          codigo: prueba.codigo || '',
          nombre: prueba.nombre || '',
          solicitadas: prueba.total_solicitadas || 0,
          completadas: prueba.total_completadas || 0,
          tiempoPromedio: prueba.tiempo_promedio || 0
        }))
        
        return {
          tests,
          summary: response.data.resumen || {
            totalSolicitadas: 0,
            totalCompletadas: 0,
            tiempoPromedio: 0
          }
        }
      } else {
        throw new Error(response.message || 'Error al obtener datos del servidor')
      }
    } catch (error) {
      console.error('Error al obtener estadísticas mensuales:', error)
      throw error
    }
  }

  async getTestDetails(entity: string, codigoPrueba: string, month: number, year: number): Promise<TestDetails> {
    try {
      // Si la entidad está vacía o es 'general', no incluir el parámetro entity
      const entityParam = entity && entity !== '' && entity !== 'general' ? `&entity=${encodeURIComponent(entity)}` : ''
      const endpoint = `${API_CONFIG.ENDPOINTS.CASOS.DETALLE_PRUEBA}/${codigoPrueba}?month=${month}&year=${year}${entityParam}`
      const response = await this.makeRequest<any>(endpoint)
      
      if (response.success && response.data) {
        // Transformar la respuesta del backend al formato esperado
        return {
          estadisticas_principales: {
            total_solicitadas: response.data.estadisticas_principales.total_solicitadas || 0,
            total_completadas: response.data.estadisticas_principales.total_completadas || 0,
            porcentaje_completado: response.data.estadisticas_principales.porcentaje_completado || 0
          },
          tiempos_procesamiento: {
            promedio_dias: response.data.tiempos_procesamiento.promedio_dias || 0,
            dentro_oportunidad: response.data.tiempos_procesamiento.dentro_oportunidad || 0,
            fuera_oportunidad: response.data.tiempos_procesamiento.fuera_oportunidad || 0,
            total_casos: response.data.tiempos_procesamiento.total_casos || 0
          },
          patologos: response.data.patologos.map((patologo: any) => ({
            nombre: patologo.nombre || '',
            codigo: patologo.codigo || '',
            total_procesadas: patologo.total_procesadas || 0,
            tiempo_promedio: patologo.tiempo_promedio || 0
          })) || []
        }
      } else {
        throw new Error(response.message || 'Error al obtener detalles de la prueba')
      }
    } catch (error) {
      console.error('Error al obtener detalles de la prueba:', error)
      throw error
    }
  }

  async getPathologists(entity: string, codigoPrueba: string, month: number, year: number): Promise<any[]> {
    try {
      const endpoint = `${API_CONFIG.ENDPOINTS.CASOS.PATOLOGOS_POR_PRUEBA}/${codigoPrueba}?month=${month}&year=${year}${entity ? `&entity=${encodeURIComponent(entity)}` : ''}`
      const response = await this.makeRequest<any>(endpoint)
      
      if (response.success && response.data) {
        return response.data.map((patologo: any) => ({
          nombre: patologo.nombre || '',
          codigo: patologo.codigo || '',
          total_procesadas: patologo.total_procesadas || 0,
          tiempo_promedio: patologo.tiempo_promedio || 0
        }))
      } else {
        throw new Error(response.message || 'Error al obtener patólogos')
      }
    } catch (error) {
      console.error('Error al obtener patólogos:', error)
      throw error
    }
  }

  async getEntities(): Promise<EntitySelection[]> {
    try {
      // Usar el endpoint de entidades del backend
      const endpoint = API_CONFIG.ENDPOINTS.CASOS.ESTADISTICAS_ENTIDADES
      const response = await this.makeRequest<any>(endpoint)
      
      if (response.entities) {
        return response.entities.map((entidad: any) => ({
          codigo: entidad.codigo || '',
          nombre: entidad.nombre || ''
        }))
      } else {
        // No hay entidades en la respuesta
        return []
      }
    } catch (error) {
      console.error('Error al obtener entidades:', error)
      // No usar datos hardcodeados, devolver lista vacía
      return []
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

export const testsApiService = new TestsApiService()