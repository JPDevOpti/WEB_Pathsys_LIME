import { ref, computed } from 'vue'
import { auxiliaryEditService } from '../services/auxiliaryEditService'
import type {
  AuxiliaryEditFormModel,
  AuxiliaryEditFormValidation
} from '../types/auxiliary.types'

export const useAuxiliaryEdition = () => {
  const isLoading = ref(false)
  const emailValidationError = ref('')
  const originalData = ref<AuxiliaryEditFormModel | null>(null)

  const canSubmit = computed(() => !emailValidationError.value)

  const validateForm = (form: AuxiliaryEditFormModel): AuxiliaryEditFormValidation => {
    const errors: AuxiliaryEditFormValidation['errors'] = {}

    if (!form.auxiliarName?.trim()) {
      errors.auxiliarName = 'El nombre es requerido'
    } else if (form.auxiliarName.trim().length < 2) {
      errors.auxiliarName = 'El nombre debe tener al menos 2 caracteres'
    } else if (form.auxiliarName.trim().length > 100) {
      errors.auxiliarName = 'El nombre no puede exceder 100 caracteres'
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
      errors.AuxiliarEmail = 'Formato de email inválido'
    }

    if (form.observaciones && form.observaciones.trim().length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  const update = async (form: AuxiliaryEditFormModel) => {
    isLoading.value = true
    try {
      const data = auxiliaryEditService.prepareUpdateData(form)
      const result = await auxiliaryEditService.updateByCode(form.auxiliarCode, data)
      if (result.success && result.data) {
        // Los datos ya vienen normalizados del servicio
        originalData.value = {
          id: result.data.id,
          auxiliarName: result.data.auxiliar_name, // Convertir snake_case a camelCase para el frontend
          auxiliarCode: result.data.auxiliar_code,
          AuxiliarEmail: result.data.auxiliar_email,
          observaciones: result.data.observaciones,
          isActive: result.data.is_active
        }
      }
      return result
    } finally {
      isLoading.value = false
    }
  }

  const setInitialData = (data: AuxiliaryEditFormModel) => { originalData.value = { ...data } }
  const resetToOriginal = () => (originalData.value ? { ...originalData.value } : null)
  const clearMessages = () => { emailValidationError.value = '' }

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
    isLoading,
    emailValidationError,
    canSubmit,
    validateForm,
    update,
    setInitialData,
    resetToOriginal,
    clearMessages,
    createHasChanges
  }
}


