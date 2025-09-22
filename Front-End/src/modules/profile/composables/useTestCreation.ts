import { ref, reactive, computed } from 'vue'
import { testCreateService } from '../services/testCreateService'
import type { 
  TestFormModel, 
  TestCreateRequest, 
  TestCreationState,
  TestFormValidation 
} from '../types/test.types'

export function useTestCreation() {
  const state = reactive<TestCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const isCheckingCode = ref(false)
  const codeValidationError = ref('')

  const canSubmit = computed(() => true)

  const validateForm = (formData: TestFormModel): TestFormValidation => {
    const errors: TestFormValidation['errors'] = {}

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

  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    if (!code?.trim()) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await testCreateService.checkCodeExists(code.trim())
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

  const normalizeTestData = (formData: TestFormModel): TestCreateRequest => {
    return {
      test_code: formData.testCode?.trim().toUpperCase() || '',
      name: formData.testName?.trim() || '',
      description: formData.testDescription?.trim() || '',
      time: formData.timeDays || 1,
      price: formData.price || 0,
      is_active: formData.isActive ?? true
    }
  }

  const createTest = async (formData: TestFormModel): Promise<{ success: boolean; data?: any }> => {
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }

    state.isLoading = true

    try {
      const requestData = normalizeTestData(formData)
      const response = await testCreateService.createTest(requestData)

      state.isSuccess = true
      state.successMessage = `Prueba "${response.name}" (${response.test_code}) creada exitosamente como ${response.is_active ? 'ACTIVA' : 'INACTIVA'}`

      return { 
        success: true, 
        data: response 
      }

    } catch (error: any) {
      let errorMessage = 'Error al crear la prueba'
      
      if (error.message) {
        errorMessage = error.message
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.status) {
        const statusMessages = {
          409: 'Ya existe una prueba con los datos proporcionados',
          422: 'Los datos proporcionados no son válidos',
          400: 'Datos incorrectos o incompletos',
          500: 'Error interno del servidor. Inténtelo más tarde'
        }
        errorMessage = statusMessages[error.response.status as keyof typeof statusMessages] || `Error del servidor (${error.response.status})`
      }
      
      state.error = errorMessage
      state.isSuccess = false
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    isCheckingCode.value = false
    codeValidationError.value = ''
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
    codeValidationError: readonly(codeValidationError),
    canSubmit,
    validateForm,
    checkCodeAvailability,
    createTest,
    clearState,
    clearMessages
  }
}

function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
