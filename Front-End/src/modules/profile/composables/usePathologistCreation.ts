// Pathologist creation composable: client-side validation, uniqueness checks,
// payload normalization (camelCase -> snake_case), and API orchestration
import { ref, reactive, computed } from 'vue'
import { pathologistCreateService } from '../services/pathologistCreateService'
import type { 
  PathologistFormModel, 
  PathologistCreateRequest, 
  PathologistCreationState,
  PathologistFormValidation
} from '../types/pathologist.types'

export function usePathologistCreation() {
  // UI feedback state shared with forms
  const state = reactive<PathologistCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Async flags and validation messages for uniqueness checks
  const isCheckingCode = ref(false)
  const isCheckingEmail = ref(false)
  const isCheckingLicense = ref(false)
  const codeValidationError = ref('')
  const emailValidationError = ref('')
  const licenseValidationError = ref('')

  // Product decision: always allow submit button (errors shown inline/banner)
  const canSubmit = computed(() => true)

  // Reusable helpers
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const isEmailValid = (email: string) => EMAIL_REGEX.test(email)
  const trimOrEmpty = (v?: string) => (v ?? '').toString().trim()

  // Client-side schema validation
  const validateForm = (formData: PathologistFormModel): PathologistFormValidation => {
    const errors: PathologistFormValidation['errors'] = {}

    if (!formData.patologoName?.trim()) {
      errors.patologoName = 'El nombre es requerido'
    } else if (formData.patologoName.length > 200) {
      errors.patologoName = 'El nombre no puede tener más de 200 caracteres'
    }
    if (!formData.InicialesPatologo?.trim()) {
      errors.InicialesPatologo = 'Las iniciales son requeridas'
    } else if (formData.InicialesPatologo.length > 10) {
      errors.InicialesPatologo = 'Las iniciales no pueden tener más de 10 caracteres'
    }
    if (!formData.patologoCode?.trim()) {
      errors.patologoCode = 'El código es requerido'
    } else if (formData.patologoCode.length > 11) {
      errors.patologoCode = 'El código no puede tener más de 11 caracteres'
    }
    if (!formData.PatologoEmail?.trim()) {
      errors.PatologoEmail = 'El email es requerido'
    } else if (!isEmailValid(formData.PatologoEmail)) {
      errors.PatologoEmail = 'El email debe tener un formato válido'
    }
    if (!formData.registro_medico?.trim()) {
      errors.registro_medico = 'El registro médico es requerido'
    } else if (formData.registro_medico.length > 50) {
      errors.registro_medico = 'El registro médico no puede tener más de 50 caracteres'
    }
    if (!formData.password?.trim()) {
      errors.password = 'La contraseña es requerida'
    }
    if (formData.observaciones && formData.observaciones.length > 500) {
      errors.observaciones = 'Máximo 500 caracteres'
    }
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  // Backend check: pathologist code uniqueness
  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    const normalized = trimOrEmpty(code)
    if (!normalized || normalized.length > 10) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await pathologistCreateService.checkCodeExists(normalized)
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

  // Backend check: email uniqueness
  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    const normalized = trimOrEmpty(email)
    if (!normalized || !isEmailValid(normalized)) return true

    isCheckingEmail.value = true
    emailValidationError.value = ''

    try {
      const exists = await pathologistCreateService.checkEmailExists(normalized)
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

  // Backend check: medical license uniqueness
  const checkMedicalLicenseAvailability = async (license: string): Promise<boolean> => {
    const normalized = trimOrEmpty(license)
    if (!normalized || normalized.length > 50) return true

    isCheckingLicense.value = true
    licenseValidationError.value = ''

    try {
      const exists = await pathologistCreateService.checkMedicalLicenseExists(normalized)
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

  // Normalize form data to backend request shape
  const normalizePathologistData = (formData: PathologistFormModel): PathologistCreateRequest => {
    return {
      pathologist_name: trimOrEmpty(formData.patologoName),
      initials: trimOrEmpty(formData.InicialesPatologo).toUpperCase(),
      pathologist_code: trimOrEmpty(formData.patologoCode).toUpperCase(),
      pathologist_email: trimOrEmpty(formData.PatologoEmail),
      medical_license: trimOrEmpty(formData.registro_medico),
      password: trimOrEmpty(formData.password),
      signature: trimOrEmpty((formData as any).firma),
      observations: trimOrEmpty(formData.observaciones),
      is_active: formData.isActive ?? true
    }
  }

  // Main flow: validate -> uniqueness -> send -> reflect UI state
  const createPathologist = async (formData: PathologistFormModel): Promise<{ success: boolean; data?: any }> => {
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }
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
      const pathologistData = normalizePathologistData(formData)
      const response = await pathologistCreateService.createPathologist(pathologistData)
      state.isSuccess = true
      state.successMessage = `Patólogo "${response.pathologist_name}" (${response.pathologist_code}) creado exitosamente como ${response.is_active ? 'ACTIVO' : 'INACTIVO'}`
      return { success: true, data: response }
    } catch (err: any) {
      let message = err?.message || err?.response?.data?.detail || ''
      if (!message && err?.response?.status) {
        const s = err.response.status
        message = s === 409 ? 'Ya existe un patólogo con los datos proporcionados'
          : s === 422 ? 'Los datos proporcionados no son válidos'
          : s === 400 ? 'Datos incorrectos o incompletos'
          : s === 500 ? 'Error interno del servidor. Inténtelo más tarde'
          : `Error del servidor (${s})`
      }
      state.error = message || 'Error al crear el patólogo'
      state.isSuccess = false
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }
  // Reset all state flags and messages
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
  // Clear only messages (keep any ongoing loading if needed)
  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
    emailValidationError.value = ''
    licenseValidationError.value = ''
  }

  return {
    // State
    state,
    isCheckingCode: readonly(isCheckingCode),
    isCheckingEmail: readonly(isCheckingEmail),
    isCheckingLicense: readonly(isCheckingLicense),
    codeValidationError: readonly(codeValidationError),
    emailValidationError: readonly(emailValidationError),
    licenseValidationError: readonly(licenseValidationError),
    canSubmit,

    // Methods
    validateForm,
    checkCodeAvailability,
    checkEmailAvailability,
    checkMedicalLicenseAvailability,
    createPathologist,
    clearState,
    clearMessages
  }
}
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
