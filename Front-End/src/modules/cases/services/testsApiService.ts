import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestDetails, TestSearchParams, TestListResponse } from '../types/test'

/**
 * Servicio para manejar operaciones con pruebas médicas
 */
class TestsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS
  
  /**
   * Transformar datos del backend al formato del frontend
   */
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
  
  /**
   * Obtener lista de pruebas con filtros y paginación
   */
  async getTests(params: TestSearchParams = {}): Promise<TestListResponse> {
    try {
      const searchParams = new URLSearchParams()
      
      if (params.query) searchParams.append('query', params.query)
      if (params.activo !== undefined) searchParams.append('activo', params.activo.toString())
      if (params.skip !== undefined) searchParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) searchParams.append('limit', params.limit.toString())
      
      console.log(`[DEBUG] Llamando a endpoint: ${this.endpoint}/?${searchParams.toString()}`)
      
      const response = await apiClient.get(`${this.endpoint}/?${searchParams.toString()}`)
      
      console.log('[DEBUG] Respuesta recibida:', response)
      
      // Validar y normalizar la respuesta
      if (!response) {
        console.error('[DEBUG] Response es null/undefined')
        throw new Error('Respuesta vacía del servidor')
      }
      
      const data = response
      
      console.log('[DEBUG] Data extraída:', data)
      
      // Si la respuesta es un array directamente
      if (Array.isArray(data)) {
        console.log('[DEBUG] Data es un array, devolviendo estructura normalizada')
        return {
          pruebas: data,
          total: data.length,
          skip: 0,
          limit: data.length,
          has_next: false,
          has_prev: false
        }
      }
      
      // Si la respuesta tiene la estructura esperada
      if (data.pruebas && Array.isArray(data.pruebas)) {
        console.log('[DEBUG] Data tiene estructura pruebas, transformando datos...')
        
        // Transformar los datos del backend al formato del frontend
        const transformedPruebas = data.pruebas.map((prueba: any) => this.transformTestData(prueba))
        
        console.log('[DEBUG] Pruebas transformadas:', transformedPruebas)
        
        return {
          pruebas: transformedPruebas,
          total: data.total || data.pruebas.length,
          skip: data.skip || 0,
          limit: data.limit || data.pruebas.length,
          has_next: data.has_next || false,
          has_prev: data.has_prev || false
        }
      }
      
      // Buscar cualquier array en la respuesta
      const dataKeys = Object.keys(data)
      console.log('[DEBUG] Claves disponibles en data:', dataKeys)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) {
          console.log(`[DEBUG] Encontrado array en clave: ${key}`)
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
      
      // Si no se encuentra ningún array, devolver respuesta vacía
      console.log('[DEBUG] No se encontró ningún array, devolviendo respuesta vacía')
      return {
        pruebas: [],
        total: 0,
        skip: 0,
        limit: 0,
        has_next: false,
        has_prev: false
      }
      
    } catch (error: any) {
      console.error('[DEBUG] Error completo en getTests:', error)
      console.error('[DEBUG] Stack trace:', error.stack)
      throw new Error(`Error al obtener pruebas: ${error.message}`)
    }
  }
  
  /**
   * Obtener todas las pruebas activas (sin paginación)
   */
  async getAllActiveTests(): Promise<TestDetails[]> {
    try {
      const response = await apiClient.get(`${this.endpoint}/?activo=true&limit=1000`)
      
      if (!response) {
        throw new Error('Respuesta vacía del servidor')
      }
      
      const data = response
      
      // Si la respuesta es un array directamente
      if (Array.isArray(data)) {
        return data
      }
      
      // Si la respuesta tiene la estructura esperada
      if (data.pruebas && Array.isArray(data.pruebas)) {
        // Transformar los datos del backend al formato del frontend
        return data.pruebas.map((prueba: any) => ({
          id: prueba.id,
          pruebaCode: prueba.prueba_code,
          pruebasName: prueba.prueba_name,
          pruebasDescription: prueba.prueba_description || '',
          tiempo: prueba.tiempo || 0,
          isActive: prueba.is_active,
          fechaCreacion: prueba.fecha_creacion,
          fechaActualizacion: prueba.fecha_actualizacion
        }))
      }
      
      // Buscar cualquier array en la respuesta
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) {
          return data[key]
        }
      }
      
      // Si no se encuentra ningún array, devolver array vacío
      return []
      
    } catch (error: any) {
      console.error('Error en getAllActiveTests:', error)
      throw new Error(`Error al obtener pruebas activas: ${error.message}`)
    }
  }
  
  /**
   * Obtiene una prueba específica por su código
   * @param pruebaCode - Código de la prueba
   * @returns Prueba encontrada
   */
  async getTestByCode(pruebaCode: string): Promise<TestDetails> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${pruebaCode}/`)
      
      if (!response) {
        throw new Error('Respuesta vacía del servidor')
      }
      
      const data = response
      
      // Si el backend devuelve directamente el objeto
      if (data && (data.prueba_code || data.prueba_name)) {
        // Transformar los datos del backend al formato del frontend
        return {
          id: data.id,
          pruebaCode: data.prueba_code,
          pruebasName: data.prueba_name,
          pruebasDescription: data.prueba_description || '',
          tiempo: data.tiempo || 0,
          isActive: data.is_active,
          fechaCreacion: data.fecha_creacion,
          fechaActualizacion: data.fecha_actualizacion
        }
      }
      
      // Si viene envuelto en otra estructura
      if (data.prueba && (data.prueba.prueba_code || data.prueba.prueba_name)) {
        const prueba = data.prueba
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
      
      // Si no se encuentra la estructura esperada
      throw new Error('Formato de respuesta inesperado para la prueba')
      
    } catch (error: any) {
      console.error('Error en getTestByCode:', error)
      throw new Error(`Error al obtener prueba por código: ${error.message}`)
    }
  }
  
  /**
   * Busca pruebas por término de búsqueda
   * @param query - Término de búsqueda
   * @param limit - Límite de resultados
   * @returns Lista de pruebas que coinciden con la búsqueda
   */
  async searchTests(query: string, limit: number = 50): Promise<TestDetails[]> {
    try {
      const response = await apiClient.get(`${this.endpoint}/?query=${encodeURIComponent(query)}&activo=true&limit=${limit}`)
      
      if (!response) {
        throw new Error('La respuesta del servidor está vacía')
      }
      
      const data = response
      
      // Si la respuesta es un array directamente
      if (Array.isArray(data)) {
        return data
      }
      
      // Si la respuesta tiene la estructura esperada
      if (data.pruebas && Array.isArray(data.pruebas)) {
        // Transformar los datos del backend al formato del frontend
        return data.pruebas.map((prueba: any) => ({
          id: prueba.id,
          pruebaCode: prueba.prueba_code,
          pruebasName: prueba.prueba_name,
          pruebasDescription: prueba.prueba_description || '',
          tiempo: prueba.tiempo || 0,
          isActive: prueba.is_active,
          fechaCreacion: prueba.fecha_creacion,
          fechaActualizacion: prueba.fecha_actualizacion
        }))
      }
      
      // Buscar cualquier array en la respuesta
      const dataKeys = Object.keys(data)
      for (const key of dataKeys) {
        if (Array.isArray(data[key])) {
          return data[key]
        }
      }
      
      // Si no se encuentra ningún array, devolver array vacío
      return []
      
    } catch (error: any) {
      console.error('Error en searchTests:', error)
      throw new Error(`Error al buscar pruebas: ${error.message}`)
    }
  }
}

export const testsApiService = new TestsApiService()
