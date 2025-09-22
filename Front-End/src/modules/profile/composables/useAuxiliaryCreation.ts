import { ref, reactive, computed } from 'vue'
import { auxiliaryCreateService } from '../services/auxiliaryCreateService'
import type { 
  AuxiliaryFormModel, 
  AuxiliaryCreateRequest, 
  AuxiliaryCreationState,
  AuxiliaryFormValidation
} from '../types/auxiliary.types'

export function useAuxiliaryCreation() {
  const state = reactive<AuxiliaryCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const isCheckingCode = ref(false)
  const isCheckingEmail = ref(false)
  const codeValidationError = ref('')
  const emailValidationError = ref('')

  const canSubmit = computed(() => true)

  const validateForm = (formData: AuxiliaryFormModel): AuxiliaryFormValidation => {
    const errors: AuxiliaryFormValidation['errors'] = {}

    if (!formData.auxiliarName?.trim()) {
      errors.auxiliarName = 'El nombre es requerido'
    } else if (formData.auxiliarName.trim().length < 2) {
      errors.auxiliarName = 'El nombre debe tener al menos 2 caracteres'
    } else if (formData.auxiliarName.trim().length > 200) {
      errors.auxiliarName = 'El nombre no puede exceder 200 caracteres'
    }

    if (!formData.auxiliarCode?.trim()) {
      errors.auxiliarCode = 'El código es requerido'
    } else if (formData.auxiliarCode.trim().length < 3) {
      errors.auxiliarCode = 'El código debe tener al menos 3 caracteres'
    } else if (formData.auxiliarCode.trim().length > 20) {
      errors.auxiliarCode = 'El código no puede exceder 20 caracteres'
    }

    if (!formData.AuxiliarEmail?.trim()) {
      errors.AuxiliarEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.AuxiliarEmail.trim())) {
      errors.AuxiliarEmail = 'El email debe tener un formato válido'
    }

    if (!formData.password?.trim()) {
      errors.password = 'La contraseña es requerida'
    } else if (formData.password.length < 6) {
      errors.password = 'La contraseña debe tener al menos 6 caracteres'
    } else if (formData.password.length > 128) {
      errors.password = 'La contraseña no puede exceder 128 caracteres'
    }

    if (formData.observaciones && formData.observaciones.trim().length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    return { isValid: Object.keys(errors).length === 0, errors }
  }


  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    if (!email?.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return true
    isCheckingEmail.value = true
    emailValidationError.value = ''
    try {
      const exists = await auxiliaryCreateService.checkEmailExists(email.trim())
      if (exists) {
        emailValidationError.value = 'Este email ya está en uso'
        return false
      }
      return true
    } catch {
      emailValidationError.value = 'Error al verificar el email'
      return false
    } finally {
      isCheckingEmail.value = false
    }
  }

  const normalizeAuxiliaryData = (formData: AuxiliaryFormModel): AuxiliaryCreateRequest => ({
    auxiliar_name: formData.auxiliarName?.trim() || '',
    auxiliar_code: formData.auxiliarCode?.trim().toUpperCase() || '',
    auxiliar_email: formData.AuxiliarEmail?.trim() || '',
    password: formData.password?.trim() || '',
    observaciones: formData.observaciones?.trim() || '',
    is_active: formData.isActive ?? true
  })

  const createAuxiliary = async (formData: AuxiliaryFormModel): Promise<{ success: boolean; data?: any }> => {
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    const validation = validateForm(formData)
    if (!validation.isValid) {
      state.error = Object.values(validation.errors).filter(Boolean).join(', ')
      return { success: false }
    }

    state.isLoading = true

    try {
      const auxiliaryData = normalizeAuxiliaryData(formData)
      const response = await auxiliaryCreateService.createAuxiliary(auxiliaryData)

      state.isSuccess = true
      state.successMessage = `Auxiliar "${response.auxiliar_name}" (${response.auxiliar_code}) creado exitosamente como ${response.is_active ? 'ACTIVO' : 'INACTIVO'}`

      return { success: true, data: response }
    } catch (err: any) {
      console.error('Error creating auxiliary:', err)
      
      let errorMessage = 'Error al crear el auxiliar'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      } else if (err.response?.status) {
        switch (err.response.status) {
          case 409: errorMessage = 'Ya existe un auxiliar con los datos proporcionados'; break
          case 422: errorMessage = 'Los datos proporcionados no son válidos'; break
          case 400: errorMessage = 'Datos incorrectos o incompletos'; break
          case 500: errorMessage = 'Error interno del servidor. Inténtelo más tarde'; break
          default: errorMessage = `Error del servidor (${err.response.status})`
        }
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
    isCheckingEmail.value = false
    codeValidationError.value = ''
    emailValidationError.value = ''
  }

  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
    emailValidationError.value = ''
  }

  return {
    state,
    isCheckingCode: computed(() => isCheckingCode.value),
    isCheckingEmail: computed(() => isCheckingEmail.value),
    codeValidationError: computed(() => codeValidationError.value),
    emailValidationError: computed(() => emailValidationError.value),
    canSubmit,
    validateForm,
    checkEmailAvailability,
    createAuxiliary,
    clearState,
    clearMessages
  }
}
