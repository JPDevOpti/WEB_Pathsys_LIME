import { ref, reactive, computed } from 'vue'
import { testCreateService } from '../services/testCreateService'
import type { 
  TestFormModel, 
  TestCreateRequest, 
  TestCreationState,
  TestFormValidation 
} from '../types/test.types'

/**
 * Composable para manejar la creación de pruebas médicas
 */
export function useTestCreation() {
  // Estado reactivo
  const state = reactive<TestCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Estados adicionales
  const isCheckingCode = ref(false)
  const codeValidationError = ref('')

  /**
   * Estado computed para verificar si se puede enviar el formulario
   */
  const canSubmit = computed(() => {
    // ✅ SIEMPRE HABILITADO: El botón de guardar nunca se bloquea
    return true
  })

  /**
   * Validar formulario en el cliente
   */
  const validateForm = (formData: TestFormModel): TestFormValidation => {
    const errors: TestFormValidation['errors'] = {}

    // Validar código
    if (!formData.pruebaCode?.trim()) {
      errors.pruebaCode = 'El código es requerido'
    } else if (formData.pruebaCode.length < 3) {
      errors.pruebaCode = 'El código debe tener al menos 3 caracteres'
    } else if (!/^[A-Z0-9_-]+$/i.test(formData.pruebaCode)) {
      errors.pruebaCode = 'Solo letras, números, guiones y guiones bajos'
    }

    // Validar nombre
    if (!formData.pruebasName?.trim()) {
      errors.pruebasName = 'El nombre es requerido'
    } else if (formData.pruebasName.length < 3) {
      errors.pruebasName = 'El nombre debe tener al menos 3 caracteres'
    }

    // Validar descripción
    if (!formData.pruebasDescription?.trim()) {
      errors.pruebasDescription = 'La descripción es requerida'
    } else if (formData.pruebasDescription.length < 10) {
      errors.pruebasDescription = 'Mínimo 10 caracteres'
    }

    // Validar tiempo (en días)
    if (!formData.tiempo || formData.tiempo <= 0) {
      errors.tiempo = 'Ingresa un tiempo válido en días'
    } else if (formData.tiempo > 365) {
      errors.tiempo = 'Máximo 365 días'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * Verificar si un código ya existe
   */
  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    if (!code?.trim() || code.length < 3) return true

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

  /**
   * Crear una nueva prueba
   */
  const createTest = async (formData: TestFormModel): Promise<{ success: boolean; data?: any }> => {
    // Limpiar estados previos
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    // Validar formulario
    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }

    // ✅ REMOVIDO: Verificación de disponibilidad de datos únicos
    // Ahora permitimos que el usuario envíe el formulario y vea el error específico del backend

    state.isLoading = true

    try {
      // Preparar datos para envío
      const requestData: TestCreateRequest = {
        pruebaCode: formData.pruebaCode.trim(),
        pruebasName: formData.pruebasName.trim(),
        pruebasDescription: formData.pruebasDescription.trim(),
        tiempo: formData.tiempo || 1, // días
        isActive: formData.isActive
      }

      // Enviar al backend
      const response = await testCreateService.createTest(requestData)

      // Manejar éxito
      state.isSuccess = true
      state.successMessage = `Prueba "${response.pruebasName}" creada exitosamente`

      return { 
        success: true, 
        data: response 
      }

    } catch (error: any) {
      // Manejar error con mensajes más específicos
      let errorMessage = 'Error al crear la prueba'
      
      if (error.message) {
        // Usar el mensaje específico del backend si está disponible
        errorMessage = error.message
      } else if (error.response?.data?.detail) {
        // Usar el detalle de la respuesta si está disponible
        errorMessage = error.response.data.detail
      } else if (error.response?.status) {
        // Mensajes específicos por código de estado
        switch (error.response.status) {
          case 409:
            errorMessage = 'Ya existe una prueba con los datos proporcionados'
            break
          case 422:
            errorMessage = 'Los datos proporcionados no son válidos'
            break
          case 400:
            errorMessage = 'Datos incorrectos o incompletos'
            break
          case 500:
            errorMessage = 'Error interno del servidor. Inténtelo más tarde'
            break
          default:
            errorMessage = `Error del servidor (${error.response.status})`
        }
      }
      
      state.error = errorMessage
      state.isSuccess = false
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  /**
   * Limpiar todos los estados
   */
  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    isCheckingCode.value = false
    codeValidationError.value = ''
  }

  /**
   * Limpiar solo mensajes (mantener loading states)
   */
  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
  }

  return {
    // Estado
    state,
    isCheckingCode: readonly(isCheckingCode),
    codeValidationError: readonly(codeValidationError),
    canSubmit,

    // Métodos
    validateForm,
    checkCodeAvailability,
    createTest,
    clearState,
    clearMessages
  }
}

// Helper para readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
