import { ref, reactive, computed } from 'vue'
import type { UserProfile, ProfileEditPayload, ValidationError } from '../types/userProfile.types'

/**
 * Composable for profile editing functionality
 */
export function useProfileEdit(user: UserProfile) {
  const isLoading = ref(false)
  const errors = ref<ValidationError[]>([])

  // Form data for different roles
  const adminForm = reactive({
    firstName: user.firstName,
    lastName: user.lastName,
    email: user.email
  })

  const patologoForm = reactive({
    patologoName: `${user.firstName} ${user.lastName}`.trim(),
    InicialesPatologo: user.roleSpecificData?.iniciales || '',
    PatologoEmail: user.email,
    registro_medico: user.roleSpecificData?.registroMedico || '',
    password: '',
    passwordConfirm: '',
    observaciones: user.roleSpecificData?.observaciones || ''
  })

  const residenteForm = reactive({
    residenteName: `${user.firstName} ${user.lastName}`.trim(),
    InicialesResidente: user.roleSpecificData?.iniciales || '',
    ResidenteEmail: user.email,
    registro_medico: user.roleSpecificData?.registroMedico || '',
    password: '',
    passwordConfirm: '',
    observaciones: user.roleSpecificData?.observaciones || ''
  })

  const auxiliarForm = reactive({
    auxiliarName: `${user.firstName} ${user.lastName}`.trim(),
    AuxiliarEmail: user.email,
    password: '',
    passwordConfirm: '',
    observaciones: user.roleSpecificData?.observaciones || ''
  })

  const facturacionForm = reactive({
    facturacionName: `${user.firstName} ${user.lastName}`.trim(),
    FacturacionEmail: user.email,
    password: '',
    passwordConfirm: '',
    observaciones: user.roleSpecificData?.observaciones || ''
  })

  // Original state for change detection
  const originalState = JSON.stringify({ 
    adminForm, patologoForm, residenteForm, auxiliarForm, facturacionForm 
  })

  const hasChanges = computed(() => 
    JSON.stringify({ adminForm, patologoForm, residenteForm, auxiliarForm, facturacionForm }) !== originalState
  )

  /**
   * Validate password fields
   */
  const validatePasswords = (password: string, passwordConfirm: string): boolean => {
    // If password is empty, no validation needed
    if (!password || !password.trim()) {
      return true
    }
    
    if (password.length < 6) {
      errors.value.push({ field: 'password', message: 'La contraseña debe tener al menos 6 caracteres' })
      return false
    }
    if (password !== passwordConfirm) {
      errors.value.push({ field: 'passwordConfirm', message: 'Las contraseñas no coinciden' })
      return false
    }
    return true
  }

  /**
   * Get current form data based on user role
   */
  const getCurrentForm = () => {
    switch (user.role) {
      case 'patologo': return patologoForm
      case 'residente': return residenteForm
      case 'auxiliar': return auxiliarForm
      case 'facturacion': return facturacionForm
      default: return adminForm
    }
  }

  /**
   * Prepare payload for submission
   */
  const preparePayload = (): ProfileEditPayload | null => {
    errors.value = []

    switch (user.role) {
      case 'patologo':
        if (!validatePasswords(patologoForm.password, patologoForm.passwordConfirm)) return null
        const patologoPayload: any = { role: 'patologo', ...patologoForm }
        // Only include password if it's not empty
        if (!patologoForm.password || !patologoForm.password.trim()) {
          delete patologoPayload.password
          delete patologoPayload.passwordConfirm
        }
        return patologoPayload
      
      case 'residente':
        if (!validatePasswords(residenteForm.password, residenteForm.passwordConfirm)) return null
        const residentePayload: any = { role: 'residente', ...residenteForm }
        // Only include password if it's not empty
        if (!residenteForm.password || !residenteForm.password.trim()) {
          delete residentePayload.password
          delete residentePayload.passwordConfirm
        }
        return residentePayload
      
      case 'auxiliar':
        if (!validatePasswords(auxiliarForm.password, auxiliarForm.passwordConfirm)) return null
        const auxiliarPayload: any = { role: 'auxiliar', ...auxiliarForm, auxiliarCode: '' }
        // Only include password if it's not empty
        if (!auxiliarForm.password || !auxiliarForm.password.trim()) {
          delete auxiliarPayload.password
          delete auxiliarPayload.passwordConfirm
        }
        return auxiliarPayload
      
      case 'facturacion':
        if (!validatePasswords(facturacionForm.password, facturacionForm.passwordConfirm)) return null
        const facturacionPayload: any = { 
          role: 'facturacion', 
          ...facturacionForm, 
          facturacionCode: (user.roleSpecificData as any)?.facturacionCode || (user.roleSpecificData as any)?.billingCode || '' 
        }
        // Only include password if it's not empty
        if (!facturacionForm.password || !facturacionForm.password.trim()) {
          delete facturacionPayload.password
          delete facturacionPayload.passwordConfirm
        }
        return facturacionPayload
      
      default:
        return { role: 'admin', ...adminForm }
    }
  }

  /**
   * Clear form errors
   */
  const clearErrors = () => {
    errors.value = []
  }

  /**
   * Reset forms to original state
   */
  const resetForms = () => {
    Object.assign(adminForm, {
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email
    })

    Object.assign(patologoForm, {
      patologoName: `${user.firstName} ${user.lastName}`.trim(),
      InicialesPatologo: user.roleSpecificData?.iniciales || '',
      PatologoEmail: user.email,
      registro_medico: user.roleSpecificData?.registroMedico || '',
      password: '',
      passwordConfirm: '',
      observaciones: user.roleSpecificData?.observaciones || ''
    })

    Object.assign(residenteForm, {
      residenteName: `${user.firstName} ${user.lastName}`.trim(),
      InicialesResidente: user.roleSpecificData?.iniciales || '',
      ResidenteEmail: user.email,
      registro_medico: user.roleSpecificData?.registroMedico || '',
      password: '',
      passwordConfirm: '',
      observaciones: user.roleSpecificData?.observaciones || ''
    })

    Object.assign(auxiliarForm, {
      auxiliarName: `${user.firstName} ${user.lastName}`.trim(),
      AuxiliarEmail: user.email,
      password: '',
      passwordConfirm: '',
      observaciones: user.roleSpecificData?.observaciones || ''
    })

    Object.assign(facturacionForm, {
      facturacionName: `${user.firstName} ${user.lastName}`.trim(),
      FacturacionEmail: user.email,
      password: '',
      passwordConfirm: '',
      observaciones: user.roleSpecificData?.observaciones || ''
    })
  }

  return {
    // State
    isLoading,
    errors,
    hasChanges,
    
    // Forms
    adminForm,
    patologoForm,
    residenteForm,
    auxiliarForm,
    facturacionForm,
    
    // Methods
    getCurrentForm,
    preparePayload,
    validatePasswords,
    clearErrors,
    resetForms
  }
}
