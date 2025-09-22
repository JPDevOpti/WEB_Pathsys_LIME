import { ref, reactive, computed } from 'vue'
import { pathologistCreateService } from '../services/pathologistCreateService'
import type { 
  PathologistFormModel, 
  PathologistCreateRequest, 
  PathologistCreationState,
  PathologistFormValidation
} from '../types/pathologist.types'

/**
 * Composable para manejar la creación de patólogos
 */
export function usePathologistCreation() {
  // Estado reactivo
  const state = reactive<PathologistCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Estados adicionales
  const isCheckingCode = ref(false)
  const isCheckingEmail = ref(false)
  const isCheckingLicense = ref(false)
  const codeValidationError = ref('')
  const emailValidationError = ref('')
  const licenseValidationError = ref('')

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
  const validateForm = (formData: PathologistFormModel): PathologistFormValidation => {
    const errors: PathologistFormValidation['errors'] = {}

    // Validar nombre
    if (!formData.patologoName?.trim()) {
      errors.patologoName = 'El nombre es requerido'
    } else if (formData.patologoName.length > 200) {
      errors.patologoName = 'El nombre no puede tener más de 200 caracteres'
    }

    // Validar iniciales
    if (!formData.InicialesPatologo?.trim()) {
      errors.InicialesPatologo = 'Las iniciales son requeridas'
    } else if (formData.InicialesPatologo.length > 10) {
      errors.InicialesPatologo = 'Las iniciales no pueden tener más de 10 caracteres'
    }

    // Validar código
    if (!formData.patologoCode?.trim()) {
      errors.patologoCode = 'El código es requerido'
    } else if (formData.patologoCode.length > 10) {
      errors.patologoCode = 'El código no puede tener más de 10 caracteres'
    }

    // Validar email
    if (!formData.PatologoEmail?.trim()) {
      errors.PatologoEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.PatologoEmail)) {
      errors.PatologoEmail = 'El email debe tener un formato válido'
    }

    // Validar registro médico
    if (!formData.registro_medico?.trim()) {
      errors.registro_medico = 'El registro médico es requerido'
    } else if (formData.registro_medico.length > 50) {
      errors.registro_medico = 'El registro médico no puede tener más de 50 caracteres'
    }

    // Validar contraseña
    if (!formData.password?.trim()) {
      errors.password = 'La contraseña es requerida'
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
    if (!code?.trim() || code.length > 10) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await pathologistCreateService.checkCodeExists(code.trim())
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
      const exists = await pathologistCreateService.checkEmailExists(email.trim())
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
   * Verificar si un registro médico ya existe
   */
  const checkMedicalLicenseAvailability = async (license: string): Promise<boolean> => {
    if (!license?.trim() || license.length > 50) return true

    isCheckingLicense.value = true
    licenseValidationError.value = ''

    try {
      const exists = await pathologistCreateService.checkMedicalLicenseExists(license.trim())
      if (exists) {
        licenseValidationError.value = 'Este registro médico ya está en uso'
        return false
      }
      return true
    } catch (error: any) {
      licenseValidationError.value = 'Error al verificar el registro médico'
      return false
    } finally {
      isCheckingLicense.value = false
    }
  }

  /**
   * Normalizar datos del formulario para que sean compatibles con el backend (snake_case)
   */
  const normalizePathologistData = (formData: PathologistFormModel): PathologistCreateRequest => {
    return {
      pathologist_name: formData.patologoName?.trim() || '',
      initials: formData.InicialesPatologo?.trim().toUpperCase() || '',
      pathologist_code: formData.patologoCode?.trim().toUpperCase() || '',
      pathologist_email: formData.PatologoEmail?.trim() || '',
      medical_license: formData.registro_medico?.trim() || '',
      password: formData.password?.trim() || '',
      signature: formData.firma?.trim() || '',
      observations: formData.observaciones?.trim() || '',
      is_active: formData.isActive ?? true
    }
  }

  /**
   * Crear un nuevo patólogo
   */
  const createPathologist = async (formData: PathologistFormModel): Promise<{ success: boolean; data?: any }> => {
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

    // Verificar disponibilidad de datos únicos
    const isCodeAvailable = await checkCodeAvailability(formData.patologoCode)
    const isEmailAvailable = await checkEmailAvailability(formData.PatologoEmail)
    const isLicenseAvailable = await checkMedicalLicenseAvailability(formData.registro_medico)

    if (!isCodeAvailable || !isEmailAvailable || !isLicenseAvailable) {
      const errors = []
      if (codeValidationError.value) errors.push(codeValidationError.value)
      if (emailValidationError.value) errors.push(emailValidationError.value)
      if (licenseValidationError.value) errors.push(licenseValidationError.value)
      state.error = errors.join(', ')
      return { success: false }
    }

    state.isLoading = true

    try {
      // Preparar datos para patólogo normalizados al formato del backend
      const pathologistData = normalizePathologistData(formData)

      // Enviar al backend
      const response = await pathologistCreateService.createPathologist(pathologistData)

      // Manejar éxito
      state.isSuccess = true
      state.successMessage = `Patólogo "${response.pathologist_name}" (${response.pathologist_code}) creado exitosamente como ${response.is_active ? 'ACTIVO' : 'INACTIVO'}`

      return { 
        success: true, 
        data: response 
      }

    } catch (err: any) {
      // Manejar error con mensajes más específicos
      let errorMessage = 'Error al crear el patólogo'
      
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
            errorMessage = 'Ya existe un patólogo con los datos proporcionados'
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
    isCheckingLicense.value = false
    codeValidationError.value = ''
    emailValidationError.value = ''
    licenseValidationError.value = ''
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
    licenseValidationError.value = ''
  }

  return {
    // Estado
    state,
    isCheckingCode: readonly(isCheckingCode),
    isCheckingEmail: readonly(isCheckingEmail),
    isCheckingLicense: readonly(isCheckingLicense),
    codeValidationError: readonly(codeValidationError),
    emailValidationError: readonly(emailValidationError),
    licenseValidationError: readonly(licenseValidationError),
    canSubmit,

    // Métodos
    validateForm,
    checkCodeAvailability,
    checkEmailAvailability,
    checkMedicalLicenseAvailability,
    createPathologist,
    clearState,
    clearMessages
  }
}

// Helper para readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
