/**
 * Composable para la edición de residentes
 */
import { ref, computed } from 'vue'
import { residentEditService } from '../services/residentEditService'
import type { 
  ResidentEditFormModel, 
  ResidentEditFormValidation
} from '../types/resident.types'

export const useResidentEdition = () => {
  // Estados reactivos
  const isLoading = ref(false)
  const codeValidationError = ref('')
  const emailValidationError = ref('')
  const licenseValidationError = ref('')
  const originalResidentData = ref<ResidentEditFormModel | null>(null)

  // Computed para verificar si se puede enviar
  const canSubmit = computed(() => {
    return !codeValidationError.value && 
           !emailValidationError.value && 
           !licenseValidationError.value
  })

  /**
   * Valida el formulario de edición
   */
  const validateForm = (formData: ResidentEditFormModel): ResidentEditFormValidation => {
    const errors: ResidentEditFormValidation['errors'] = {}

    // Validación del nombre
    if (!formData.residenteName?.trim()) {
      errors.residenteName = 'El nombre es requerido'
    } else if (formData.residenteName.trim().length < 2) {
      errors.residenteName = 'El nombre debe tener al menos 2 caracteres'
    } else if (formData.residenteName.trim().length > 100) {
      errors.residenteName = 'El nombre no puede exceder 100 caracteres'
    }

    // Validación de iniciales
    if (!formData.InicialesResidente?.trim()) {
      errors.InicialesResidente = 'Las iniciales son requeridas'
    } else if (formData.InicialesResidente.trim().length < 2) {
      errors.InicialesResidente = 'Las iniciales deben tener al menos 2 caracteres'
    } else if (formData.InicialesResidente.trim().length > 10) {
      errors.InicialesResidente = 'Las iniciales no pueden exceder 10 caracteres'
    }

    // Validación del código
    if (!formData.residenteCode?.trim()) {
      errors.residenteCode = 'El código es requerido'
    } else if (formData.residenteCode.trim().length < 3) {
      errors.residenteCode = 'El código debe tener al menos 3 caracteres'
    } else if (formData.residenteCode.trim().length > 20) {
      errors.residenteCode = 'El código no puede exceder 20 caracteres'
    }

    // Validación del email
    if (!formData.ResidenteEmail?.trim()) {
      errors.ResidenteEmail = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.ResidenteEmail.trim())) {
      errors.ResidenteEmail = 'Formato de email inválido'
    }

    // Validación del registro médico
    if (!formData.registro_medico?.trim()) {
      errors.registro_medico = 'El registro médico es requerido'
    } else if (formData.registro_medico.trim().length < 3) {
      errors.registro_medico = 'El registro médico debe tener al menos 3 caracteres'
    } else if (formData.registro_medico.trim().length > 50) {
      errors.registro_medico = 'El registro médico no puede exceder 50 caracteres'
    }

    // Validación de observaciones (opcional)
    if (formData.observaciones && formData.observaciones.trim().length > 500) {
      errors.observaciones = 'Las observaciones no pueden exceder 500 caracteres'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * Verifica disponibilidad del código
   */
  const checkCodeAvailability = async (code: string) => {
    if (!originalResidentData.value) return
    
    codeValidationError.value = ''
    
    if (!code?.trim()) {
      codeValidationError.value = 'El código es requerido'
      return
    }

    if (code.trim().length < 3) {
      codeValidationError.value = 'Mínimo 3 caracteres'
      return
    }

    if (code.trim().length > 20) {
      codeValidationError.value = 'Máximo 20 caracteres'
      return
    }

    try {
      const result = await residentEditService.checkCodeExists(code.trim(), originalResidentData.value.residenteCode)
      if (!result.available) {
        codeValidationError.value = result.error || 'Código no disponible'
      }
    } catch (error) {
      codeValidationError.value = 'Error al verificar código'
    }
  }

  /**
   * Verifica disponibilidad del email
   */
  const checkEmailAvailability = async (email: string) => {
    if (!originalResidentData.value) return
    
    emailValidationError.value = ''
    
    if (!email?.trim()) {
      emailValidationError.value = 'El email es requerido'
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      emailValidationError.value = 'Formato de email inválido'
      return
    }

    try {
      const result = await residentEditService.checkEmailExists(email.trim(), originalResidentData.value.ResidenteEmail)
      if (!result.available) {
        emailValidationError.value = result.error || 'Email no disponible'
      }
    } catch (error) {
      emailValidationError.value = 'Error al verificar email'
    }
  }

  /**
   * Verifica disponibilidad del registro médico
   */
  const checkLicenseAvailability = async (license: string) => {
    if (!originalResidentData.value) return
    
    licenseValidationError.value = ''
    
    if (!license?.trim()) {
      licenseValidationError.value = 'El registro médico es requerido'
      return
    }

    if (license.trim().length < 3) {
      licenseValidationError.value = 'Mínimo 3 caracteres'
      return
    }

    if (license.trim().length > 50) {
      licenseValidationError.value = 'Máximo 50 caracteres'
      return
    }

    try {
      const result = await residentEditService.checkLicenseExists(license.trim(), originalResidentData.value.registro_medico)
      if (!result.available) {
        licenseValidationError.value = result.error || 'Registro médico no disponible'
      }
    } catch (error) {
      licenseValidationError.value = 'Error al verificar registro médico'
    }
  }

  /**
   * Actualiza un residente
   */
  const updateResident = async (formData: ResidentEditFormModel) => {
    isLoading.value = true
    
    try {
      const updateData = residentEditService.prepareUpdateData(formData)
      const result = await residentEditService.updateResident(formData.residenteCode, updateData)
      
      if (result.success && result.data) {
        // Normalizar datos del backend antes de usarlos
        const normalizedData = residentEditService.normalizeResidentData(result.data)
        
        // Actualizar datos originales para futuras comparaciones
        originalResidentData.value = {
          id: normalizedData.id,
          residenteName: normalizedData.residenteName,
          InicialesResidente: normalizedData.InicialesResidente,
          residenteCode: normalizedData.residenteCode,
          ResidenteEmail: normalizedData.ResidenteEmail,
          registro_medico: normalizedData.registro_medico,
          observaciones: normalizedData.observaciones,
          isActive: normalizedData.isActive
        }
        
        return {
          success: true,
          data: normalizedData
        }
      }
      
      return result
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Error al actualizar residente'
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Establece los datos iniciales del residente
   */
  const setInitialData = (residentData: ResidentEditFormModel) => {
    originalResidentData.value = { ...residentData }
  }

  /**
   * Resetea al estado original
   */
  const resetToOriginal = (): ResidentEditFormModel | null => {
    return originalResidentData.value ? { ...originalResidentData.value } : null
  }

  /**
   * Limpia todos los estados
   */
  const clearState = () => {
    isLoading.value = false
    originalResidentData.value = null
    clearMessages()
  }

  /**
   * Limpia solo los mensajes de error
   */
  const clearMessages = () => {
    codeValidationError.value = ''
    emailValidationError.value = ''
    licenseValidationError.value = ''
  }

  /**
   * Función para detectar cambios comparando con datos originales
   */
  const createHasChanges = (currentData: ResidentEditFormModel) => {
    if (!originalResidentData.value) return false
    
    const passwordChanged = !!currentData.password && currentData.password.trim().length >= 6

    return (
      originalResidentData.value.residenteName !== currentData.residenteName ||
      originalResidentData.value.InicialesResidente !== currentData.InicialesResidente ||
      originalResidentData.value.residenteCode !== currentData.residenteCode ||
      originalResidentData.value.ResidenteEmail !== currentData.ResidenteEmail ||
      originalResidentData.value.registro_medico !== currentData.registro_medico ||
      originalResidentData.value.observaciones !== currentData.observaciones ||
      originalResidentData.value.isActive !== currentData.isActive ||
      passwordChanged
    )
  }

  return {
    // Estados
    isLoading,
    codeValidationError,
    emailValidationError,
    licenseValidationError,
    canSubmit,

    // Métodos
    validateForm,
    checkCodeAvailability,
    checkEmailAvailability,
    checkLicenseAvailability,
    updateResident,
    setInitialData,
    resetToOriginal,
    clearState,
    clearMessages,
    createHasChanges
  }
}
