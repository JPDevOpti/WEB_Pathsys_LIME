import { ref, reactive, computed } from 'vue'
import { testEditService } from '../services/testEditService'
import type { 
  TestEditFormModel, 
  TestEditionState,
  TestEditFormValidation 
} from '../types/test.types'

export function useTestEdition() {
  const state = reactive<TestEditionState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const isCheckingCode = ref(false)
  const isLoadingTest = ref(false)
  const codeValidationError = ref('')
  const originalTestData = ref<TestEditFormModel | null>(null)

  const canSubmit = computed(() => {
    return !state.isLoading && !isCheckingCode.value && !isLoadingTest.value
  })

  const validateForm = (formData: TestEditFormModel): TestEditFormValidation => {
    const errors: TestEditFormValidation['errors'] = {}

    if (!formData.testCode?.trim()) {
      errors.testCode = 'El código es requerido'
    } else if (!/^[A-Z0-9_-]+$/i.test(formData.testCode)) {
      errors.testCode = 'Solo letras, números, guiones y guiones bajos'
    }

    if (!formData.testName?.trim()) {
      errors.testName = 'El nombre es requerido'
    }

    if (!formData.testDescription?.trim()) {
      errors.testDescription = 'La descripción es requerida'
    }

    if (!formData.timeDays || formData.timeDays <= 0) {
      errors.timeDays = 'Ingresa un tiempo válido en días'
    } else if (formData.timeDays > 365) {
      errors.timeDays = 'Máximo 365 días'
    }

    if (formData.price === undefined || formData.price === null) {
      errors.price = 'El precio es requerido'
    } else if (formData.price < 0) {
      errors.price = 'El precio no puede ser negativo'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  const loadTestForEdition = async (testCode: string): Promise<{ success: boolean; data?: TestEditFormModel }> => {
    isLoadingTest.value = true
    state.error = ''

    try {
      const testData = await testEditService.getTestByCode(testCode)
      originalTestData.value = { ...testData }
      
      return { 
        success: true, 
        data: testData 
      }
    } catch (error: any) {
      state.error = error.message || 'Error al cargar los datos de la prueba'
      return { success: false }
    } finally {
      isLoadingTest.value = false
    }
  }

  const checkCodeAvailability = async (code: string, originalCode?: string): Promise<boolean> => {
    if (!code?.trim() || code.length < 3) return true
    if (originalCode && code.trim() === originalCode) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await testEditService.checkCodeExists(code.trim(), originalCode)
      if (exists) {
        codeValidationError.value = 'Este código ya está en uso'
        return false
      }
      return true
    } catch (error: any) {
      codeValidationError.value = 'Error al verificar el código'
      return false
    } finally {
      isCheckingCode.value = false
    }
  }

  const createHasChanges = (currentData: TestEditFormModel) => {
    if (!originalTestData.value) return false
    
    return (
      originalTestData.value.testCode !== currentData.testCode ||
      originalTestData.value.testName !== currentData.testName ||
      originalTestData.value.testDescription !== currentData.testDescription ||
      originalTestData.value.timeDays !== currentData.timeDays ||
      originalTestData.value.price !== currentData.price ||
      originalTestData.value.isActive !== currentData.isActive
    )
  }

  const normalizeTestData = (formData: TestEditFormModel) => {
    return {
      test_code: formData.testCode?.trim().toUpperCase() || '',
      name: formData.testName?.trim() || '',
      description: formData.testDescription?.trim() || '',
      time: formData.timeDays || 1,
      price: formData.price || 0,
      is_active: formData.isActive ?? true
    }
  }

  const updateTest = async (formData: TestEditFormModel): Promise<{ success: boolean; data?: any }> => {
    if (!originalTestData.value) {
      state.error = 'No se han cargado los datos originales de la prueba'
      return { success: false }
    }

    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }

    if (formData.testCode !== originalTestData.value.testCode) {
      const isCodeAvailable = await checkCodeAvailability(formData.testCode, originalTestData.value.testCode)
      if (!isCodeAvailable) {
        state.error = codeValidationError.value || 'Código no disponible'
        return { success: false }
      }
    }

    state.isLoading = true

    try {
      const updateData = normalizeTestData(formData)
      const response = await testEditService.updateTest(originalTestData.value.testCode, updateData)

      originalTestData.value = {
        id: response._id,
        testCode: response.test_code,
        testName: response.name,
        testDescription: response.description,
        timeDays: response.time,
        price: response.price,
        isActive: response.is_active
      }

      state.isSuccess = true
      state.successMessage = `Prueba "${response.name}" actualizada exitosamente`

      return { 
        success: true, 
        data: response 
      }

    } catch (error: any) {
      state.error = error.message || 'Error al actualizar la prueba'
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  const setInitialData = (testData: TestEditFormModel): void => {
    originalTestData.value = { ...testData }
  }

  const resetToOriginal = (): TestEditFormModel | null => {
    return originalTestData.value ? { ...originalTestData.value } : null
  }

  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    isCheckingCode.value = false
    isLoadingTest.value = false
    codeValidationError.value = ''
    originalTestData.value = null
  }

  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
  }

  return {
    state,
    isCheckingCode: readonly(isCheckingCode),
    isLoadingTest: readonly(isLoadingTest),
    codeValidationError: readonly(codeValidationError),
    originalTestData: readonly(originalTestData),
    canSubmit,
    validateForm,
    loadTestForEdition,
    checkCodeAvailability,
    updateTest,
    setInitialData,
    resetToOriginal,
    clearState,
    clearMessages,
    createHasChanges
  }
}

function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
