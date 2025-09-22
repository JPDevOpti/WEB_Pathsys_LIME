import { ref, reactive } from 'vue'
import { billingCreateService } from '../services/billingCreateService'
import type { 
  BillingFormModel, 
  BillingFormValidation,
  BillingCreateRequest,
  BillingCreationState
} from '../types/billing.types'

export function useBillingCreation() {
  // Local state for request/feedback
  const state = reactive<BillingCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const emailValidationError = ref('')
  const isCheckingEmail = ref(false)

  // Helpers
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const isEmailValid = (email: string) => EMAIL_REGEX.test(email)
  const trimOrEmpty = (value?: string) => (value?.trim() ?? '')

  const validateForm = (formData: BillingFormModel): BillingFormValidation => {
    const name = trimOrEmpty(formData.billingName)
    const code = trimOrEmpty(formData.billingCode)
    const email = trimOrEmpty(formData.billingEmail)
    const password = trimOrEmpty(formData.password)
    const observations = formData.observations || ''

    const errors: BillingFormValidation['errors'] = {}

    if (!name) errors.billingName = 'El nombre es requerido'
    else if (name.length < 2) errors.billingName = 'El nombre debe tener al menos 2 caracteres'
    else if (name.length > 200) errors.billingName = 'El nombre no puede exceder 200 caracteres'

    if (!code) errors.billingCode = 'El código es requerido'
    else if (code.length < 3) errors.billingCode = 'El código debe tener al menos 3 caracteres'
    else if (code.length > 20) errors.billingCode = 'El código no puede exceder 20 caracteres'

    if (!email) errors.billingEmail = 'El email es requerido'
    else if (!isEmailValid(email)) errors.billingEmail = 'El email no tiene un formato válido'

    if (!password) errors.password = 'La contraseña es requerida'
    else if (password.length < 6) errors.password = 'La contraseña debe tener al menos 6 caracteres'
    else if (password.length > 128) errors.password = 'La contraseña no puede exceder 128 caracteres'

    if (observations && observations.length > 500) errors.observations = 'Las observaciones no pueden exceder 500 caracteres'

    return { isValid: Object.keys(errors).length === 0, errors }
  }

  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    const normalized = trimOrEmpty(email)
    if (!normalized) return true
    isCheckingEmail.value = true
    emailValidationError.value = ''

    try {
      const exists = await billingCreateService.checkEmailExists(normalized)
      if (exists) { emailValidationError.value = 'Este email ya está en uso'; return false }
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
    billing_name: trimOrEmpty(formData.billingName),
    billing_code: trimOrEmpty(formData.billingCode),
    billing_email: trimOrEmpty(formData.billingEmail),
    password: formData.password,
    observations: trimOrEmpty(formData.observations),
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

      const emailAvailable = await checkEmailAvailability(formData.billingEmail)
      if (!emailAvailable) { state.error = 'El email ya está en uso'; return { success: false } }

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
