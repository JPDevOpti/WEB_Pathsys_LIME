import { ref } from 'vue'
import { testsApiService } from '../services/testsApiService'
import type { TestDetails, TestOperationResult } from '../types'

// Estado global compartido para todas las instancias
let globalTests = ref<TestDetails[]>([])
let globalIsLoading = ref(false)
let globalError = ref('')
let loadPromise: Promise<TestOperationResult> | null = null

export function useTestAPI() {
  const tests = globalTests
  const isLoading = globalIsLoading
  const error = globalError

  const loadTests = async (): Promise<TestOperationResult> => {
    // Si ya hay una carga en progreso, esperar a que termine
    if (loadPromise) {
      return loadPromise
    }

    // Si ya tenemos pruebas cargadas, no volver a cargar
    if (tests.value.length > 0) {
      return { success: true, tests: tests.value }
    }

    isLoading.value = true
    error.value = ''

    loadPromise = (async () => {
      try {
        console.log('useTestAPI: Cargando pruebas desde el servidor...')
        // Usar el límite máximo permitido por el backend (100)
        const response = await testsApiService.getTests({ limit: 100 })
        tests.value = response.pruebas || []
        console.log('useTestAPI: Pruebas cargadas:', tests.value.length)
        return { success: true, tests: tests.value }
      } catch (err: any) {
        error.value = err.message || 'Error al cargar las pruebas'
        console.error('useTestAPI: Error al cargar pruebas:', err)
        return { success: false, error: error.value }
      } finally {
        isLoading.value = false
        loadPromise = null
      }
    })()

    return loadPromise
  }

  const clearState = () => {
    tests.value = []
    error.value = ''
    isLoading.value = false
    loadPromise = null
  }

  return {
    tests, isLoading, error, loadTests, clearState
  }
}
