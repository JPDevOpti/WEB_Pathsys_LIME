import { ref, reactive } from 'vue'
import { facturacionCreateService } from '../services/facturacionCreateService'
import type { 
  FacturacionFormModel, 
  FacturacionFormValidation,
  FacturacionCreateRequest,
  FacturacionCreationState
} from '../types/facturacion.types'

export function useFacturacionCreation() {
  // Estado reactivo
  const state = reactive<FacturacionCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Errores de validación específicos
  const codeValidationError = ref('')
  const emailValidationError = ref('')

  // Estado de verificación
  const isCheckingCode = ref(false)
  const isCheckingEmail = ref(false)

  /**
   * Validar formulario de facturación
   */
  const validateForm = (formData: FacturacionFormModel): FacturacionFormValidation => {
    const errors: FacturacionFormValidation['errors'] = {}

    // Validar nombre
    if (!formData.facturacionName?.trim()) {
      errors.facturacionName = 'El nombre es requerido'
    } else if (formData.facturacionName.length < 2) {
      errors.facturacionName = 'El nombre debe tener al menos 2 caracteres'
    } else if (formData.facturacionName.length > 200) {
      errors.facturacionName = 'El nombre no puede exceder 200 caracteres'
    }

    // Validar código
    if (!formData.facturacionCode?.trim()) {
      errors.facturacionCode = 'El código es requerido'
    } else if (formData.facturacionCode.length < 3) {
      errors.facturacionCode = 'El código debe tener al menos 3 caracteres'
    } else if (formData.facturacionCode.length > 20) {
      errors.facturacionCode = 'El código no puede exceder 20 caracteres'
    }

    // Validar email
    if (!formData.FacturacionEmail?.trim()) {
      errors.FacturacionEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.FacturacionEmail)) {
      errors.FacturacionEmail = 'El email no tiene un formato válido'
    }

    // Validar contraseña
    if (!formData.password?.trim()) {
      errors.password = 'La contraseña es requerida'
    } else if (formData.password.length < 6) {
      errors.password = 'La contraseña debe tener al menos 6 caracteres'
    } else if (formData.password.length > 128) {
      errors.password = 'La contraseña no puede exceder 128 caracteres'
    }

    // Validar observaciones
    if (formData.observaciones && formData.observaciones.length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * Verificar disponibilidad del código
   */
  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    if (!code?.trim()) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await facturacionCreateService.checkCodeExists(code)
      if (exists) {
        codeValidationError.value = 'Este código ya está en uso'
        return false
      }
      return true
    } catch (error) {
      console.error('Error checking code availability:', error)
      codeValidationError.value = 'Error al verificar el código'
      return false
    } finally {
      isCheckingCode.value = false
    }
  }

  /**
   * Verificar disponibilidad del email
   */
  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    if (!email?.trim()) return true

    isCheckingEmail.value = true
    emailValidationError.value = ''

    try {
      const exists = await facturacionCreateService.checkEmailExists(email)
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

  /**
   * Normalizar datos del formulario para el backend
   */
  const normalizeFacturacionData = (formData: FacturacionFormModel): FacturacionCreateRequest => {
    return {
      facturacion_name: formData.facturacionName.trim(),
      facturacion_code: formData.facturacionCode.trim(),
      facturacion_email: formData.FacturacionEmail.trim(),
      password: formData.password,
      observaciones: formData.observaciones?.trim() || '',
      is_active: formData.isActive
    }
  }

  /**
   * Crear usuario de facturación
   */
  const createFacturacion = async (formData: FacturacionFormModel): Promise<{ success: boolean; data?: any }> => {
    state.isLoading = true
    state.error = ''
    state.successMessage = ''

    try {
      // Validar formulario
      const validation = validateForm(formData)
      if (!validation.isValid) {
        state.error = 'Por favor, corrija los errores en el formulario'
        return { success: false }
      }

      // Verificar disponibilidad del código
      const codeAvailable = await checkCodeAvailability(formData.facturacionCode)
      if (!codeAvailable) {
        state.error = 'El código ya está en uso'
        return { success: false }
      }

      // Verificar disponibilidad del email
      const emailAvailable = await checkEmailAvailability(formData.FacturacionEmail)
      if (!emailAvailable) {
        state.error = 'El email ya está en uso'
        return { success: false }
      }

      // Normalizar datos
      const facturacionData = normalizeFacturacionData(formData)

      // Crear usuario de facturación
      const result = await facturacionCreateService.createFacturacion(facturacionData)
      
      console.log('🔍 RESULTADO DEL SERVICIO:', result)
      console.log('🔍 Tipo del resultado:', typeof result)
      console.log('🔍 Es null?', result === null)
      console.log('🔍 Es undefined?', result === undefined)

      state.isSuccess = true
      state.successMessage = 'Usuario de facturación creado exitosamente'

      const finalResult = { success: true, data: result }
      console.log('🔍 RESULTADO FINAL DEL COMPOSABLE:', finalResult)
      return finalResult
    } catch (error: any) {
      console.error('Error creating facturacion:', error)
      // No establecer state.error aquí, dejar que el error se propague
      throw error
    } finally {
      state.isLoading = false
    }
  }

  /**
   * Limpiar estado
   */
  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    codeValidationError.value = ''
    emailValidationError.value = ''
    isCheckingCode.value = false
    isCheckingEmail.value = false
  }

  /**
   * Limpiar solo mensajes
   */
  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    codeValidationError.value = ''
    emailValidationError.value = ''
  }

  return {
    // Estado
    state,
    codeValidationError,
    emailValidationError,
    isCheckingCode,
    isCheckingEmail,

    // Métodos
    validateForm,
    checkCodeAvailability,
    checkEmailAvailability,
    createFacturacion,
    clearState,
    clearMessages
  }
}
