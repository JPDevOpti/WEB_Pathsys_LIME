import { ref, reactive, computed } from 'vue'
import { residentCreateService } from '../services/residentCreateService'
import type { 
  ResidentFormModel, 
  ResidentCreateRequest, 
  ResidentCreationState,
  ResidentFormValidation
} from '../types/resident.types'

/**
 * Composable para manejar la creación de residentes
 */
export function useResidentCreation() {
  // Estado reactivo
  const state = reactive<ResidentCreationState>({
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
  const validateForm = (formData: ResidentFormModel): ResidentFormValidation => {
    const errors: ResidentFormValidation['errors'] = {}

    // Validar nombre
    if (!formData.residenteName?.trim()) {
      errors.residenteName = 'El nombre es requerido'
    } else if (formData.residenteName.length < 2) {
      errors.residenteName = 'El nombre debe tener al menos 2 caracteres'
    } else if (formData.residenteName.length > 100) {
      errors.residenteName = 'El nombre no puede tener más de 100 caracteres'
    }

    // Validar iniciales
    if (!formData.InicialesResidente?.trim()) {
      errors.InicialesResidente = 'Las iniciales son requeridas'
    } else if (formData.InicialesResidente.length < 2) {
      errors.InicialesResidente = 'Las iniciales deben tener al menos 2 caracteres'
    } else if (formData.InicialesResidente.length > 10) {
      errors.InicialesResidente = 'Las iniciales no pueden tener más de 10 caracteres'
    }

    // Validar código
    if (!formData.residenteCode?.trim()) {
      errors.residenteCode = 'El código es requerido'
    } else if (formData.residenteCode.length < 3) {
      errors.residenteCode = 'El código debe tener al menos 3 caracteres'
    } else if (formData.residenteCode.length > 20) {
      errors.residenteCode = 'El código no puede tener más de 20 caracteres'
    }

    // Validar email
    if (!formData.ResidenteEmail?.trim()) {
      errors.ResidenteEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.ResidenteEmail)) {
      errors.ResidenteEmail = 'El email debe tener un formato válido'
    }

    // Validar registro médico
    if (!formData.registro_medico?.trim()) {
      errors.registro_medico = 'El registro médico es requerido'
    } else if (formData.registro_medico.length < 3) {
      errors.registro_medico = 'El registro médico debe tener al menos 3 caracteres'
    } else if (formData.registro_medico.length > 50) {
      errors.registro_medico = 'El registro médico no puede tener más de 50 caracteres'
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
      const exists = await residentCreateService.checkCodeExists(code.trim())
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
      const exists = await residentCreateService.checkEmailExists(email.trim())
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
    if (!license?.trim() || license.length < 3) return true

    isCheckingLicense.value = true
    licenseValidationError.value = ''

    try {
      const exists = await residentCreateService.checkMedicalLicenseExists(license.trim())
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
   * Crear un nuevo residente
   */
  const createResident = async (formData: ResidentFormModel): Promise<{ success: boolean; data?: any }> => {
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
    const isCodeAvailable = await checkCodeAvailability(formData.residenteCode)
    const isEmailAvailable = await checkEmailAvailability(formData.ResidenteEmail)
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
      // Preparar datos para residente (incluyendo password)
      const residentData: ResidentCreateRequest = {
        residenteName: formData.residenteName.trim(),
        InicialesResidente: formData.InicialesResidente.trim().toUpperCase(),
        residenteCode: formData.residenteCode.trim().toUpperCase(),
        ResidenteEmail: formData.ResidenteEmail.trim(),
        registro_medico: formData.registro_medico.trim(),
        password: formData.password.trim(), // Incluir contraseña para crear usuario
        observaciones: formData.observaciones.trim(),
        isActive: formData.isActive
      }

      // Enviar al backend
      const response = await residentCreateService.createResident(residentData)

      // Manejar éxito
      state.isSuccess = true
      state.successMessage = `Residente "${response.residenteName}" creado exitosamente`

      return { 
        success: true, 
        data: response  // ✅ Ahora response ya son los datos correctos
      }

    } catch (err: any) {
      // Manejar error con mensajes más específicos
      let errorMessage = 'Error al crear el residente'
      
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
            errorMessage = 'Ya existe un residente con los datos proporcionados'
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
    createResident,
    clearState,
    clearMessages
  }
}

// Helper para readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
