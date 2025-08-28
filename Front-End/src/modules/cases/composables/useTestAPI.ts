import { ref } from 'vue'
import { testsApiService } from '../services/testsApiService'
import type { TestDetails, TestOperationResult } from '../types'

export function useTestAPI() {
  const tests = ref<TestDetails[]>([])
  const isLoading = ref(false)
  const error = ref('')

  const loadTests = async (): Promise<TestOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await testsApiService.getTests()
      
      // Actualizar el estado local con las pruebas cargadas
      tests.value = response.pruebas || []
      
      return {
        success: true,
        tests: tests.value
      }
    } catch (err: any) {
      error.value = err.message || 'Error al cargar las pruebas'
      
      return {
        success: false,
        error: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  const searchTests = async (query: string): Promise<TestOperationResult> => {
    if (!query.trim()) {
      return await loadTests()
    }

    isLoading.value = true
    error.value = ''

    try {
      const results = await testsApiService.searchTests(query)
      
      // Actualizar el estado local con los resultados de búsqueda
      tests.value = results || []
      
      return {
        success: true,
        tests: tests.value
      }
    } catch (err: any) {
      error.value = err.message || 'Error al buscar pruebas'
      
      return {
        success: false,
        error: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  const getTestByCode = async (pruebaCode: string): Promise<TestOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const test = await testsApiService.getTestByCode(pruebaCode)
      
      if (test) {
        return {
          success: true,
          test
        }
      } else {
        return {
          success: false,
          error: 'Prueba no encontrada'
        }
      }
    } catch (err: any) {
      error.value = err.message || 'Error al obtener la prueba'
      
      return {
        success: false,
        error: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  const clearState = () => {
    tests.value = []
    error.value = ''
    isLoading.value = false
  }

  return {
    tests,
    isLoading,
    error,
    loadTests,
    searchTests,
    getTestByCode,
    clearState
  }
}
