import { ref, reactive } from 'vue'
import { billingCreateService } from '../services/billingCreateService'
import type { 
  BillingFormModel, 
  BillingFormValidation,
  BillingCreateRequest,
  BillingCreationState
} from '../types/billing.types'

export function useBillingCreation() {
  const state = reactive<BillingCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const emailValidationError = ref('')
  const isCheckingEmail = ref(false)

  const validateForm = (formData: BillingFormModel): BillingFormValidation => {
    const errors: BillingFormValidation['errors'] = {}

    if (!formData.facturacionName?.trim()) {
      errors.facturacionName = 'El nombre es requerido'
    } else if (formData.facturacionName.length < 2) {
      errors.facturacionName = 'El nombre debe tener al menos 2 caracteres'
    } else if (formData.facturacionName.length > 200) {
      errors.facturacionName = 'El nombre no puede exceder 200 caracteres'
    }

    if (!formData.facturacionCode?.trim()) {
      errors.facturacionCode = 'El código es requerido'
    } else if (formData.facturacionCode.length < 3) {
      errors.facturacionCode = 'El código debe tener al menos 3 caracteres'
    } else if (formData.facturacionCode.length > 20) {
      errors.facturacionCode = 'El código no puede exceder 20 caracteres'
    }

    if (!formData.FacturacionEmail?.trim()) {
      errors.FacturacionEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.FacturacionEmail)) {
      errors.FacturacionEmail = 'El email no tiene un formato válido'
    }

    if (!formData.password?.trim()) {
      errors.password = 'La contraseña es requerida'
    } else if (formData.password.length < 6) {
      errors.password = 'La contraseña debe tener al menos 6 caracteres'
    } else if (formData.password.length > 128) {
      errors.password = 'La contraseña no puede exceder 128 caracteres'
    }

    if (formData.observaciones && formData.observaciones.length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    return { isValid: Object.keys(errors).length === 0, errors }
  }

  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    if (!email?.trim()) return true

    isCheckingEmail.value = true
    emailValidationError.value = ''

    try {
      const exists = await billingCreateService.checkEmailExists(email)
      if (exists) {
        emailValidationError.value = 'Este email ya está en uso'
        return false
      }
      return true
    } catch (error) {
      console.error('Error checking email availability:', error)
      emailValidationError.value = 'Error al verificar el email'
      return false
    } finally {
      isCheckingEmail.value = false
    }
  }

  const normalizeFacturacionData = (formData: BillingFormModel): BillingCreateRequest => ({
    billing_name: formData.facturacionName.trim(),
    billing_code: formData.facturacionCode.trim(),
    billing_email: formData.FacturacionEmail.trim(),
    password: formData.password,
    observations: formData.observaciones?.trim() || '',
    is_active: formData.isActive
  })

  const createFacturacion = async (formData: BillingFormModel): Promise<{ success: boolean; data?: any }> => {
    state.isLoading = true
    state.error = ''
    state.successMessage = ''

    try {
      const validation = validateForm(formData)
      if (!validation.isValid) {
        state.error = 'Por favor, corrija los errores en el formulario'
        return { success: false }
      }

      const emailAvailable = await checkEmailAvailability(formData.FacturacionEmail)
      if (!emailAvailable) {
        state.error = 'El email ya está en uso'
        return { success: false }
      }

      const facturacionData = normalizeFacturacionData(formData)
      const result = await billingCreateService.createFacturacion(facturacionData)

      state.isSuccess = true
      state.successMessage = 'Usuario de facturación creado exitosamente'

      return { success: true, data: result }
    } catch (error: any) {
      console.error('Error creating facturacion:', error)
      throw error
    } finally {
      state.isLoading = false
    }
  }

  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    emailValidationError.value = ''
    isCheckingEmail.value = false
  }

  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    emailValidationError.value = ''
  }

  return {
    state,
    emailValidationError,
    isCheckingEmail,
    validateForm,
    checkEmailAvailability,
    createFacturacion,
    clearState,
    clearMessages
  }
}
