import { ref, reactive, computed } from 'vue'
import { residentCreateService } from '../services/residentCreateService'
import type { ResidentFormModel, ResidentCreateRequest, ResidentCreationState, ResidentFormValidation } from '../types/resident.types'

export function useResidentCreation() {
  const state = reactive<ResidentCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })
  const isCheckingCode = ref(false)
  const isCheckingEmail = ref(false)
  const isCheckingLicense = ref(false)
  const codeValidationError = ref('')
  const emailValidationError = ref('')
  const licenseValidationError = ref('')
  const canSubmit = computed(() => true)

  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const isEmailValid = (email: string) => EMAIL_REGEX.test(email)
  const trimOrEmpty = (v?: string) => (v ?? '').toString().trim()

  const validateForm = (formData: ResidentFormModel): ResidentFormValidation => {
    const errors: ResidentFormValidation['errors'] = {}

    if (!formData.residenteName?.trim()) {
      errors.residenteName = 'El nombre es requerido'
    } else if (formData.residenteName.length > 100) {
      errors.residenteName = 'El nombre no puede tener más de 100 caracteres'
    }
    if (!formData.InicialesResidente?.trim()) {
      errors.InicialesResidente = 'Las iniciales son requeridas'
    } else if (formData.InicialesResidente.length > 10) {
      errors.InicialesResidente = 'Las iniciales no pueden tener más de 10 caracteres'
    }
    if (!formData.residenteCode?.trim()) {
      errors.residenteCode = 'El código es requerido'
    } else if (formData.residenteCode.length > 20) {
      errors.residenteCode = 'El código no puede tener más de 20 caracteres'
    }
    if (!formData.ResidenteEmail?.trim()) {
      errors.ResidenteEmail = 'El email es requerido'
    } else if (!isEmailValid(formData.ResidenteEmail)) {
      errors.ResidenteEmail = 'El email debe tener un formato válido'
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
  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    const normalized = trimOrEmpty(code)
    if (!normalized || normalized.length < 3 || normalized.length > 20) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await residentCreateService.checkCodeExists(normalized)
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

  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    const normalized = trimOrEmpty(email)
    if (!normalized || !isEmailValid(normalized)) return true

    isCheckingEmail.value = true
    emailValidationError.value = ''

    try {
      const exists = await residentCreateService.checkEmailExists(normalized)
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

  const checkMedicalLicenseAvailability = async (license: string): Promise<boolean> => {
    const normalized = trimOrEmpty(license)
    if (!normalized || normalized.length < 3) return true

    isCheckingLicense.value = true
    licenseValidationError.value = ''

    try {
      const exists = await residentCreateService.checkMedicalLicenseExists(normalized)
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

  const normalizeResidentData = (formData: ResidentFormModel): ResidentCreateRequest => {
    return {
      resident_name: trimOrEmpty(formData.residenteName),
      initials: trimOrEmpty(formData.InicialesResidente).toUpperCase(),
      resident_code: trimOrEmpty(formData.residenteCode).toUpperCase(),
      resident_email: trimOrEmpty(formData.ResidenteEmail),
      medical_license: trimOrEmpty(formData.registro_medico),
      password: trimOrEmpty(formData.password),
      observations: trimOrEmpty(formData.observaciones),
      is_active: formData.isActive ?? true
    }
  }
  const createResident = async (formData: ResidentFormModel): Promise<{ success: boolean; data?: any }> => {
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''
    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }
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
      const residentData = normalizeResidentData(formData)
      const response = await residentCreateService.createResident(residentData)
      state.isSuccess = true
      state.successMessage = `Residente "${response.resident_name}" (${response.resident_code}) creado exitosamente como ${response.is_active ? 'ACTIVO' : 'INACTIVO'}`
      return { success: true, data: response }
    } catch (err: any) {
      let message = err?.message || err?.response?.data?.detail || ''
      if (!message && err?.response?.status) {
        const s = err.response.status
        message = s === 409 ? 'Ya existe un residente con los datos proporcionados'
          : s === 422 ? 'Los datos proporcionados no son válidos'
          : s === 400 ? 'Datos incorrectos o incompletos'
          : s === 500 ? 'Error interno del servidor. Inténtelo más tarde'
          : `Error del servidor (${s})`
      }
      state.error = message || 'Error al crear el residente'
      state.isSuccess = false
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }
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
  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
    emailValidationError.value = ''
    licenseValidationError.value = ''
  }

  return {
    state,
    isCheckingCode: readonly(isCheckingCode),
    isCheckingEmail: readonly(isCheckingEmail),
    isCheckingLicense: readonly(isCheckingLicense),
    codeValidationError: readonly(codeValidationError),
    emailValidationError: readonly(emailValidationError),
    licenseValidationError: readonly(licenseValidationError),
    canSubmit,
    validateForm,
    checkCodeAvailability,
    checkEmailAvailability,
    checkMedicalLicenseAvailability,
    createResident,
    clearState,
    clearMessages
  }
}
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
