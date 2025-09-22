// Billing edition composable: validates edit form, prepares payloads, updates via API,
// and exposes helpers to track original data and UI messages. Keep field names aligned
// with BillingEditFormModel (billingName, billingEmail, observations, billingCode).
import { ref, reactive } from 'vue'
import { billingEditService } from '../services/billingEditService'
import type { 
  BillingEditFormModel,
  BillingEditFormValidation,
  BillingEditionState
} from '../types/billing.types'

export const useBillingEdition = () => {
  // Request/feedback state used by UI
  const state = reactive<BillingEditionState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const emailValidationError = ref('')
  const originalData = ref<BillingEditFormModel | null>(null)

  // Helpers (keep consistent with creation composable)
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const isEmailValid = (email: string) => EMAIL_REGEX.test(email)
  const trimOrEmpty = (value?: string) => (value?.trim() ?? '')

  // Validate the edition form. Password is optional but must meet rules if provided.
  const validateForm = (form: BillingEditFormModel): BillingEditFormValidation => {
    const errors: BillingEditFormValidation['errors'] = {}

    const name = trimOrEmpty(form.billingName)
    const email = trimOrEmpty(form.billingEmail)
    const observations = form.observations || ''
    const pwd = trimOrEmpty(form.password)
    const pwdConfirm = trimOrEmpty(form.passwordConfirm)

    if (!name) errors.billingName = 'El nombre es requerido'
    else if (name.length < 2) errors.billingName = 'El nombre debe tener al menos 2 caracteres'
    else if (name.length > 200) errors.billingName = 'El nombre no puede exceder 200 caracteres'

    if (!email) errors.billingEmail = 'El email es requerido'
    else if (!isEmailValid(email)) errors.billingEmail = 'El email no tiene un formato válido'

    if (observations && observations.length > 500) {
      errors.observations = 'Las observaciones no pueden exceder 500 caracteres'
    }

    if (pwd.length > 0) {
      if (pwd.length < 6) errors.password = 'La contraseña debe tener al menos 6 caracteres'
      else if (pwd.length > 128) errors.password = 'La contraseña no puede exceder 128 caracteres'
      if (pwd !== pwdConfirm) errors.passwordConfirm = 'Las contraseñas no coinciden'
    }

    return { isValid: Object.keys(errors).length === 0, errors }
  }

  // Calls backend to update an existing billing user by code
  const update = async (form: BillingEditFormModel) => {
    state.isLoading = true
    state.error = ''
    state.successMessage = ''

    try {
      const validation = validateForm(form)
      if (!validation.isValid) {
        state.error = 'Por favor, corrija los errores en el formulario'
        return { success: false }
      }

      const updateData = billingEditService.prepareUpdateData(form)
      const result = await billingEditService.updateByCode(form.billingCode, updateData)

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
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar el usuario de facturación'
      state.error = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      state.isLoading = false
    }
  }

  // Store original data to compare changes or reset
  const setInitialData = (data: BillingEditFormModel) => { 
    originalData.value = { ...data } 
  }
  
  // Return a copy of original data if present
  const resetToOriginal = () => (originalData.value ? { ...originalData.value } : null)
  
  // Clear transient UI messages
  const clearMessages = () => { 
    emailValidationError.value = '' 
    state.error = ''
    state.successMessage = ''
  }

  // Compare current values against the captured originals to know if there are changes
  const createHasChanges = (current: BillingEditFormModel) => {
    if (!originalData.value) return false
    
    return (
      current.billingName !== originalData.value.billingName ||
      current.billingEmail !== originalData.value.billingEmail ||
      current.observations !== originalData.value.observations ||
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
