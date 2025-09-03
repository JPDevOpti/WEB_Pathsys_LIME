import { ref, reactive, computed } from 'vue'
import { testEditService } from '../services/testEditService'
import type { 
  TestEditFormModel, 
  TestEditionState,
  TestEditFormValidation 
} from '../types/test.types'

/**
 * Composable para manejar la edición de pruebas médicas
 */
export function useTestEdition() {
  // Estado reactivo
  const state = reactive<TestEditionState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Estados adicionales
  const isCheckingCode = ref(false)
  const isLoadingTest = ref(false)
  const codeValidationError = ref('')
  const originalTestData = ref<TestEditFormModel | null>(null)

  /**
   * Estado computed para verificar si se puede enviar el formulario
   */
  const canSubmit = computed(() => {
    return !state.isLoading && !isCheckingCode.value && !isLoadingTest.value
  })

  /**
   * Validar formulario en el cliente
   */
  const validateForm = (formData: TestEditFormModel): TestEditFormValidation => {
    const errors: TestEditFormValidation['errors'] = {}

    // Validar código
    if (!formData.pruebaCode?.trim()) {
      errors.pruebaCode = 'El código es requerido'
    } else if (!/^[A-Z0-9_-]+$/i.test(formData.pruebaCode)) {
      errors.pruebaCode = 'Solo letras, números, guiones y guiones bajos'
    }

    // Validar nombre
    if (!formData.pruebasName?.trim()) {
      errors.pruebasName = 'El nombre es requerido'
    }

    // Validar descripción
    if (!formData.pruebasDescription?.trim()) {
      errors.pruebasDescription = 'La descripción es requerida'
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
   * Cargar datos de una prueba para edición
   */
  const loadTestForEdition = async (pruebaCode: string): Promise<{ success: boolean; data?: TestEditFormModel }> => {
    isLoadingTest.value = true
    state.error = ''

    try {
      const testData = await testEditService.getTestByCode(pruebaCode)
      originalTestData.value = { ...testData } // Copia para comparar cambios
      
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

  /**
   * Verificar si un código ya existe (excluyendo el código original)
   */
  const checkCodeAvailability = async (code: string, originalCode?: string): Promise<boolean> => {
    if (!code?.trim() || code.length < 3) return true
    
    // Si es el mismo código original, no hay conflicto
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

  /**
   * Crear función para detectar cambios que reciba los datos actuales
   */
  const createHasChanges = (currentData: TestEditFormModel) => {
    if (!originalTestData.value) return false
    
    return (
      originalTestData.value.pruebaCode !== currentData.pruebaCode ||
      originalTestData.value.pruebasName !== currentData.pruebasName ||
      originalTestData.value.pruebasDescription !== currentData.pruebasDescription ||
      originalTestData.value.tiempo !== currentData.tiempo ||
      originalTestData.value.isActive !== currentData.isActive
    )
  }

  /**
   * Normalizar datos del formulario para que sean compatibles con el backend (snake_case)
   */
  const normalizeTestData = (formData: TestEditFormModel) => {
    return {
      prueba_code: formData.pruebaCode?.trim().toUpperCase() || '',
      prueba_name: formData.pruebasName?.trim() || '',
      prueba_description: formData.pruebasDescription?.trim() || '',
      tiempo: formData.tiempo || 1,
      is_active: formData.isActive ?? true
    }
  }

  /**
   * Actualizar una prueba existente
   */
  const updateTest = async (formData: TestEditFormModel): Promise<{ success: boolean; data?: any }> => {
    // Verificar que tenemos datos originales
    if (!originalTestData.value) {
      state.error = 'No se han cargado los datos originales de la prueba'
      return { success: false }
    }

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

    // Verificar código disponible si cambió
    if (formData.pruebaCode !== originalTestData.value.pruebaCode) {
      const isCodeAvailable = await checkCodeAvailability(formData.pruebaCode, originalTestData.value.pruebaCode)
      if (!isCodeAvailable) {
        state.error = codeValidationError.value || 'Código no disponible'
        return { success: false }
      }
    }

    state.isLoading = true

    try {
      // Preparar datos para actualización normalizados al formato del backend
      const updateData = normalizeTestData(formData)
      
      // Enviar al backend usando el código original
      const response = await testEditService.updateTest(originalTestData.value.pruebaCode, updateData)

      // Actualizar datos originales con los nuevos datos
      originalTestData.value = {
        id: response.id,
        pruebaCode: response.prueba_code,
        pruebasName: response.prueba_name,
        pruebasDescription: response.prueba_description,
        tiempo: response.tiempo,
        isActive: response.is_active
      }

      // Manejar éxito
      state.isSuccess = true
      state.successMessage = `Prueba "${response.prueba_name}" actualizada exitosamente`

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

  /**
   * Establecer datos iniciales desde props (para integración con sistema existente)
   */
  const setInitialData = (testData: TestEditFormModel): void => {
    originalTestData.value = { ...testData }
  }

  /**
   * Restablecer formulario a los datos originales
   */
  const resetToOriginal = (): TestEditFormModel | null => {
    return originalTestData.value ? { ...originalTestData.value } : null
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
    isLoadingTest.value = false
    codeValidationError.value = ''
    originalTestData.value = null
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
    isLoadingTest: readonly(isLoadingTest),
    codeValidationError: readonly(codeValidationError),
    originalTestData: readonly(originalTestData),
    canSubmit,

    // Métodos
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

// Helper para readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
