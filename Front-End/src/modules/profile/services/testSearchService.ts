import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

/**
 * Servicio para búsqueda de pruebas médicas
 */
class TestSearchService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  /**
   * Buscar pruebas por nombre o código
   */
  async searchTests(query: string, includeInactive: boolean = false): Promise<any[]> {
    try {
      if (!query?.trim()) {
        return []
      }

      // Búsqueda por nombre de prueba o código
      const response = await apiClient.get(`${this.endpoint}/`, {
        params: {
          query: query.trim(),
          activo: includeInactive ? undefined : true, // Solo pruebas activas si no se incluyen inactivas
          limit: 50 // Límite de resultados
        }
      })

      // Mapear respuesta del backend al formato esperado por el frontend
      if (response.pruebas && Array.isArray(response.pruebas)) {
        return response.pruebas.map((prueba: any) => ({
          id: prueba.id || prueba._id, // Asegurar que tenemos el ID
          nombre: prueba.pruebasName,
          codigo: prueba.pruebaCode,
          descripcion: prueba.pruebasDescription,
          tiempo: prueba.tiempo,
          activo: prueba.isActive,
          tipo: 'pruebas', // Tipo para el filtrado en la UI
          fecha_creacion: prueba.fecha_creacion,
          fecha_actualizacion: prueba.fecha_actualizacion
        }))
      }

      return []
    } catch (error: any) {
      console.error('Error al buscar pruebas:', error)
      
      // Si no hay resultados, devolver array vacío
      if (error.response?.status === 404) {
        return []
      }
      
      // Para otros errores, lanzar excepción
      throw new Error(error.message || 'Error al buscar pruebas')
    }
  }

  /**
   * Obtener una prueba específica por código para edición
   */
  async getTestByCode(code: string): Promise<any | null> {
    try {
      const response = await apiClient.get(`${this.endpoint}/code/${code}`)
      
      if (response) {
        return {
          id: response.id,
          nombre: response.pruebasName,
          codigo: response.pruebaCode,
          descripcion: response.pruebasDescription,
          tiempo: response.tiempo,
          activo: response.isActive,
          tipo: 'pruebas',
          fecha_creacion: response.fecha_creacion,
          fecha_actualizacion: response.fecha_actualizacion
        }
      }

      return null
    } catch (error: any) {
      console.error('Error al obtener prueba por código:', error)
      
      if (error.response?.status === 404) {
        return null
      }
      
      throw new Error(error.message || 'Error al obtener la prueba')
    }
  }
}

// Exportar instancia singleton
export const testSearchService = new TestSearchService()
export default testSearchService
