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
          activo: includeInactive ? undefined : true, // Usar 'activo' según el schema PruebaSearch
          limit: 50 // Límite de resultados
        }
      })

      // Mapear respuesta del backend al formato esperado por el frontend
      if (response.pruebas && Array.isArray(response.pruebas)) {
        return response.pruebas.map((prueba: any) => {
          // Mapeo correcto según documentación del backend
          const nombre = prueba.prueba_name || prueba.pruebasName || prueba.nombre || prueba.name || ''
          const codigo = prueba.prueba_code || prueba.pruebaCode || prueba.codigo || prueba.code || ''
          const descripcion = prueba.prueba_description || prueba.pruebasDescription || prueba.descripcion || prueba.description || ''
          const activo = prueba.is_active !== undefined ? prueba.is_active : (prueba.isActive !== undefined ? prueba.isActive : prueba.activo)
          return {
            id: prueba.id || prueba._id,
            nombre,
            codigo,
            descripcion,
            tiempo: prueba.tiempo,
            activo,
            tipo: 'pruebas',
            fecha_creacion: prueba.fecha_creacion,
            fecha_actualizacion: prueba.fecha_actualizacion
          }
        })
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
        // Mapeo correcto según documentación del backend
        const nombre = response.prueba_name || response.pruebasName || response.nombre || response.name || ''
        const codigo = response.prueba_code || response.pruebaCode || response.codigo || response.code || ''
        const descripcion = response.prueba_description || response.pruebasDescription || response.descripcion || response.description || ''
        const activo = response.is_active !== undefined ? response.is_active : (response.isActive !== undefined ? response.isActive : response.activo)
        return {
          id: response.id,
          nombre,
          codigo,
          descripcion,
          tiempo: response.tiempo,
          activo,
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
