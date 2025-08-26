import { ref } from 'vue'
import { testsApiService } from '../services/testsApiService'
import type { TestDetails, TestOperationResult } from '../types/test'

/**
 * Composable para manejar operaciones con pruebas médicas
 */
export function useTestAPI() {
  // Estado reactivo
  const tests = ref<TestDetails[]>([])
  const isLoading = ref(false)
  const error = ref('')

  /**
   * Cargar todas las pruebas activas
   */
  const loadTests = async (): Promise<TestOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const result = await testsApiService.getAllActiveTests()
      tests.value = result
      
      return {
        success: true,
        tests: result,
        message: 'Pruebas cargadas exitosamente'
      }
    } catch (err: any) {
      let errorMessage = 'Error al cargar pruebas'
      
      // Log detallado del error para debugging
      console.error('Error completo al cargar pruebas:', {
        error: err,
        response: err.response,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        message: err.message
      })
      
      if (err.response?.status === 307) {
        errorMessage = 'Error de redirección en el servidor. Verificar configuración de endpoints.'
      } else if (err.response?.data?.detail) {
        errorMessage = `Error de validación: ${JSON.stringify(err.response.data.detail)}`
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message
      } else if (err.message) {
        errorMessage = err.message
      }
      
      error.value = errorMessage
      
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Buscar pruebas por término
   */
  const searchTests = async (query: string, limit: number = 50): Promise<TestOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const result = await testsApiService.searchTests(query, limit)
      
      return {
        success: true,
        tests: result,
        message: 'Búsqueda completada'
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Error en la búsqueda'
      error.value = errorMessage
      
      console.error('Error al buscar pruebas:', err)
      
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener prueba por código
   */
  const getTestByCode = async (pruebaCode: string): Promise<TestOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const result = await testsApiService.getTestByCode(pruebaCode)
      
      return {
        success: true,
        test: result,
        message: 'Prueba encontrada'
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Prueba no encontrada'
      error.value = errorMessage
      
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Limpiar estado de errores
   */
  const clearState = () => {
    error.value = ''
  }

  return {
    // Estado
    tests,
    isLoading,
    error,
    
    // Métodos
    loadTests,
    searchTests,
    getTestByCode,
    clearState
  }
}
