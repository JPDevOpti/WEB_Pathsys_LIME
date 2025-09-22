// Tests API composable: shared cache, in-flight dedupe, simple errors
import { ref } from 'vue'
import { testsApiService } from '../services/testsApiService'
import type { TestDetails, TestOperationResult } from '../types'

// Shared reactive state across instances
let globalTests = ref<TestDetails[]>([])
let globalIsLoading = ref(false)
let globalError = ref('')
let loadPromise: Promise<TestOperationResult> | null = null

export function useTestAPI() {
  const tests = globalTests
  const isLoading = globalIsLoading
  const error = globalError

  const loadTests = async (): Promise<TestOperationResult> => {
    if (loadPromise) return loadPromise
    if (tests.value.length > 0) return { success: true, tests: tests.value }

    isLoading.value = true
    error.value = ''

    loadPromise = (async () => {
      try {
        const response = await testsApiService.getTests({ limit: 100 })
        tests.value = response.pruebas || []
        return { success: true, tests: tests.value }
      } catch (err: any) {
        error.value = err?.message || 'Error al cargar las pruebas'
        return { success: false, error: error.value }
      } finally {
        isLoading.value = false
        loadPromise = null
      }
    })()

    return loadPromise
  }

  const clearState = () => { tests.value = []; error.value = ''; isLoading.value = false; loadPromise = null }

  return { tests, isLoading, error, loadTests, clearState }
}
