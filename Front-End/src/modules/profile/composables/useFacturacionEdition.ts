import { ref, reactive } from 'vue'
import { facturacionEditService } from '../services/facturacionEditService'
import type { 
  FacturacionEditFormModel,
  FacturacionEditFormValidation,
  FacturacionEditionState
} from '../types/facturacion.types'

export const useFacturacionEdition = () => {
  const state = reactive<FacturacionEditionState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const emailValidationError = ref('')
  const originalData = ref<FacturacionEditFormModel | null>(null)

  const validateForm = (form: FacturacionEditFormModel): FacturacionEditFormValidation => {
    const errors: FacturacionEditFormValidation['errors'] = {}

    if (!form.facturacionName?.trim()) {
      errors.facturacionName = 'El nombre es requerido'
    } else if (form.facturacionName.length < 2) {
      errors.facturacionName = 'El nombre debe tener al menos 2 caracteres'
    } else if (form.facturacionName.length > 200) {
      errors.facturacionName = 'El nombre no puede exceder 200 caracteres'
    }

    if (!form.FacturacionEmail?.trim()) {
      errors.FacturacionEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.FacturacionEmail)) {
      errors.FacturacionEmail = 'El email no tiene un formato válido'
    }

    if (form.observaciones && form.observaciones.length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  const update = async (form: FacturacionEditFormModel) => {
    state.isLoading = true
    state.error = ''
    state.successMessage = ''

    try {
      const validation = validateForm(form)
      if (!validation.isValid) {
        state.error = 'Por favor, corrija los errores en el formulario'
        return { success: false }
      }

      const updateData = facturacionEditService.prepareUpdateData(form)
      const result = await facturacionEditService.updateByCode(form.facturacionCode, updateData)

      if (result.success) {
        state.isSuccess = true
        state.successMessage = 'Usuario de facturación actualizado exitosamente'
        return { success: true, data: result.data }
      } else {
        state.error = result.error || 'Error al actualizar el usuario de facturación'
        return { success: false }
      }
    } catch (error: any) {
      console.error('Error updating facturacion:', error)
      state.error = error.message || 'Error al actualizar el usuario de facturación'
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  const setInitialData = (data: FacturacionEditFormModel) => { 
    originalData.value = { ...data } 
  }
  
  const resetToOriginal = () => (originalData.value ? { ...originalData.value } : null)
  
  const clearMessages = () => { 
    emailValidationError.value = '' 
  }

  const createHasChanges = (current: FacturacionEditFormModel) => {
    if (!originalData.value) return false
    
    return (
      current.facturacionName !== originalData.value.facturacionName ||
      current.FacturacionEmail !== originalData.value.FacturacionEmail ||
      current.observaciones !== originalData.value.observaciones ||
      current.isActive !== originalData.value.isActive ||
      (current.password && current.password.trim() !== '')
    )
  }

  return {
    state,
    emailValidationError,
    validateForm,
    update,
    setInitialData,
    resetToOriginal,
    clearMessages,
    createHasChanges
  }
}
