import { ref, reactive, computed } from 'vue'
import { auxiliaryCreateService } from '../services/auxiliaryCreateService'
import type { 
  AuxiliaryFormModel, 
  AuxiliaryCreateRequest, 
  AuxiliaryCreationState,
  AuxiliaryFormValidation
} from '../types/auxiliary.types'

/**
 * Composable para manejar la creación de auxiliares
 */
export function useAuxiliaryCreation() {
  // Estado reactivo
  const state = reactive<AuxiliaryCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Estados adicionales
  const isCheckingCode = ref(false)
  const isCheckingEmail = ref(false)
  const codeValidationError = ref('')
  const emailValidationError = ref('')

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
  const validateForm = (formData: AuxiliaryFormModel): AuxiliaryFormValidation => {
    const errors: AuxiliaryFormValidation['errors'] = {}

    // Validar nombre
    if (!formData.auxiliarName?.trim()) {
      errors.auxiliarName = 'El nombre es requerido'
    } else if (formData.auxiliarName.length < 2) {
      errors.auxiliarName = 'El nombre debe tener al menos 2 caracteres'
    } else if (formData.auxiliarName.length > 100) {
      errors.auxiliarName = 'El nombre no puede tener más de 100 caracteres'
    }

    // Validar código
    if (!formData.auxiliarCode?.trim()) {
      errors.auxiliarCode = 'El código es requerido'
    } else if (formData.auxiliarCode.length < 3) {
      errors.auxiliarCode = 'El código debe tener al menos 3 caracteres'
    } else if (formData.auxiliarCode.length > 20) {
      errors.auxiliarCode = 'El código no puede tener más de 20 caracteres'
    }

    // Validar email
    if (!formData.AuxiliarEmail?.trim()) {
      errors.AuxiliarEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.AuxiliarEmail)) {
      errors.AuxiliarEmail = 'El email debe tener un formato válido'
    }

    // Validar contraseña
    if (!formData.password?.trim()) {
      errors.password = 'La contraseña es requerida'
    } else if (formData.password.length < 6) {
      errors.password = 'La contraseña debe tener al menos 6 caracteres'
    }

    // Validar observaciones (opcional)
    if (formData.observaciones && formData.observaciones.length > 500) {
      errors.observaciones = 'Máximo 500 caracteres'
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
    if (!code?.trim() || code.length < 3 || code.length > 20) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await auxiliaryCreateService.checkCodeExists(code.trim())
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
   * Verificar si un email ya existe
   */
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
    } catch (error: any) {
      emailValidationError.value = 'Error al verificar el email'
      return false
    } finally {
      isCheckingEmail.value = false
    }
  }

  /**
   * Crear un nuevo auxiliar
   */
  const createAuxiliary = async (formData: AuxiliaryFormModel): Promise<{ success: boolean; data?: any }> => {
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
      // Preparar datos para auxiliar (incluyendo password)
      const auxiliaryData: AuxiliaryCreateRequest = {
        auxiliarName: formData.auxiliarName.trim(),
        auxiliarCode: formData.auxiliarCode.trim().toUpperCase(),
        AuxiliarEmail: formData.AuxiliarEmail.trim(),
        password: formData.password.trim(), // Incluir contraseña para crear usuario
        observaciones: formData.observaciones.trim(),
        isActive: formData.isActive
      }

      // Enviar al backend
      const response = await auxiliaryCreateService.createAuxiliary(auxiliaryData)

      // Manejar éxito
      state.isSuccess = true
      state.successMessage = `Auxiliar "${response.auxiliarName}" creado exitosamente`

      return { 
        success: true, 
        data: response 
      }

    } catch (err: any) {
      // Manejar error con mensajes más específicos
      let errorMessage = 'Error al crear el auxiliar'
      
      if (err.message) {
        // Usar el mensaje específico del backend si está disponible
        errorMessage = err.message
      } else if (err.response?.data?.detail) {
        // Usar el detalle de la respuesta si está disponible
        errorMessage = err.response.data.detail
      } else if (err.response?.status) {
        // Mensajes específicos por código de estado
        switch (err.response.status) {
          case 409:
            errorMessage = 'Ya existe un auxiliar con los datos proporcionados'
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
            errorMessage = `Error del servidor (${err.response.status})`
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
    isCheckingEmail.value = false
    codeValidationError.value = ''
    emailValidationError.value = ''
  }

  /**
   * Limpiar solo mensajes (mantener loading states)
   */
  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
    emailValidationError.value = ''
  }

  return {
    // Estado
    state,
    isCheckingCode: readonly(isCheckingCode),
    isCheckingEmail: readonly(isCheckingEmail),
    codeValidationError: readonly(codeValidationError),
    emailValidationError: readonly(emailValidationError),
    canSubmit,

    // Métodos
    validateForm,
    checkCodeAvailability,
    checkEmailAvailability,
    createAuxiliary,
    clearState,
    clearMessages
  }
}

// Helper para readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
