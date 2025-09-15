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
      tests.value = response.pruebas || []
      return { success: true, tests: tests.value }
    } catch (err: any) {
      error.value = err.message || 'Error al cargar las pruebas'
      return { success: false, error: error.value }
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
    tests, isLoading, error, loadTests, clearState
  }
}
