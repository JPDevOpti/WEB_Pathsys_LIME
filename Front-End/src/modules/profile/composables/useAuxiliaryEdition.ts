import { ref, reactive, computed } from 'vue'
import { auxiliaryEditService } from '../services/auxiliaryEditService'
import type {
  AuxiliaryEditFormModel,
  AuxiliaryEditFormValidation,
  AuxiliaryEditionState
} from '../types/auxiliary.types'

export const useAuxiliaryEdition = () => {
  const state = reactive<AuxiliaryEditionState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const emailValidationError = ref('')
  const originalData = ref<AuxiliaryEditFormModel | null>(null)

  const canSubmit = computed(() => !emailValidationError.value)

  const validateForm = (form: AuxiliaryEditFormModel): AuxiliaryEditFormValidation => {
    const errors: AuxiliaryEditFormValidation['errors'] = {}

    if (!form.auxiliarName?.trim()) {
      errors.auxiliarName = 'El nombre es requerido'
    } else if (form.auxiliarName.trim().length < 2) {
      errors.auxiliarName = 'El nombre debe tener al menos 2 caracteres'
    } else if (form.auxiliarName.trim().length > 200) {
      errors.auxiliarName = 'El nombre no puede exceder 200 caracteres'
    }

    if (!form.auxiliarCode?.trim()) {
      errors.auxiliarCode = 'El código es requerido'
    } else if (form.auxiliarCode.trim().length < 3) {
      errors.auxiliarCode = 'El código debe tener al menos 3 caracteres'
    } else if (form.auxiliarCode.trim().length > 20) {
      errors.auxiliarCode = 'El código no puede exceder 20 caracteres'
    }

    if (!form.AuxiliarEmail?.trim()) {
      errors.AuxiliarEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.AuxiliarEmail.trim())) {
      errors.AuxiliarEmail = 'El email debe tener un formato válido'
    }

    if (form.observaciones && form.observaciones.trim().length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    // Validación de contraseña si se proporciona
    if (form.password && form.password.trim().length > 0) {
      if (form.password.length < 6) {
        errors.password = 'La contraseña debe tener al menos 6 caracteres'
      } else if (form.password.length > 128) {
        errors.password = 'La contraseña no puede exceder 128 caracteres'
      }
      
      if (form.passwordConfirm && form.password !== form.passwordConfirm) {
        errors.passwordConfirm = 'Las contraseñas no coinciden'
      }
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  const update = async (form: AuxiliaryEditFormModel) => {
    state.isLoading = true
    state.error = ''
    state.successMessage = ''

    try {
      const validation = validateForm(form)
      if (!validation.isValid) {
        state.error = 'Por favor, corrija los errores en el formulario'
        return { success: false }
      }

      const data = auxiliaryEditService.prepareUpdateData(form)
      const result = await auxiliaryEditService.updateByCode(form.auxiliarCode, data)
      
      if (result.success && result.data) {
        state.isSuccess = true
        state.successMessage = 'Auxiliar actualizado exitosamente'
        
        // Actualizar datos originales
        originalData.value = {
          id: result.data.id,
          auxiliarName: result.data.auxiliar_name,
          auxiliarCode: result.data.auxiliar_code,
          AuxiliarEmail: result.data.auxiliar_email,
          observaciones: result.data.observaciones,
          isActive: result.data.is_active,
          password: '',
          passwordConfirm: ''
        }
        
        return { success: true, data: result.data }
      } else {
        state.error = result.error || 'Error al actualizar el auxiliar'
        return { success: false }
      }
    } catch (error: any) {
      console.error('Error updating auxiliary:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar el auxiliar'
      state.error = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      state.isLoading = false
    }
  }

  const setInitialData = (data: AuxiliaryEditFormModel) => { 
    originalData.value = { ...data } 
  }
  
  const resetToOriginal = () => (originalData.value ? { ...originalData.value } : null)
  
  const clearMessages = () => { 
    emailValidationError.value = ''
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
  }

  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    emailValidationError.value = ''
  }

  const createHasChanges = (current: AuxiliaryEditFormModel) => {
    if (!originalData.value) return false
    const passwordChanged = !!current.password && current.password.trim().length >= 6
    return (
      originalData.value.auxiliarName !== current.auxiliarName ||
      originalData.value.auxiliarCode !== current.auxiliarCode ||
      originalData.value.AuxiliarEmail !== current.AuxiliarEmail ||
      originalData.value.observaciones !== current.observaciones ||
      originalData.value.isActive !== current.isActive ||
      passwordChanged
    )
  }

  return {
    state,
    emailValidationError,
    canSubmit,
    validateForm,
    update,
    setInitialData,
    resetToOriginal,
    clearMessages,
    clearState,
    createHasChanges
  }
}



