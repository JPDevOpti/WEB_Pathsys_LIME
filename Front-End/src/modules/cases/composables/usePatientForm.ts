import { ref, reactive } from 'vue'
import type { PatientData, PatientFormErrors, PatientFormWarnings, ValidationState } from '../types'

export function usePatientForm() {
  const formData = reactive<PatientData>({
    patientCode: '', name: '', gender: '', age: '', entity: '', careType: '', observations: ''
  })

  const validationState = reactive<ValidationState>({
    hasAttemptedSubmit: false, isValidating: false, showValidationError: false
  })

  const errors = reactive<PatientFormErrors>({ patientCode: [], name: [], age: [] })
  const warnings = reactive<PatientFormWarnings>({ patientCode: [], age: [] })
  const isLoading = ref(false)

  const validateCedula = (): boolean => {
    const cedula = formData.patientCode.trim()
    errors.patientCode = []
    warnings.patientCode = []

    if (!cedula) {
      if (validationState.hasAttemptedSubmit) errors.patientCode.push('La cédula es obligatoria')
      return false
    }

    if (!/^\d+$/.test(cedula)) {
      errors.patientCode.push('La cédula debe contener solo números')
      return false
    }

    if (cedula.length > 10) {
      errors.patientCode.push('La cédula no puede tener más de 10 dígitos')
      return false
    }

    if (cedula.length > 0 && cedula.length < 6) {
      const faltan = 6 - cedula.length
      warnings.patientCode.push(`Faltan ${faltan} dígito${faltan === 1 ? '' : 's'} para una cédula válida`)
      
      if (validationState.hasAttemptedSubmit) {
        errors.patientCode.push('La cédula debe tener al menos 6 dígitos')
        warnings.patientCode = []
        return false
      }
    }

    return true
  }

  const validateNombre = (): boolean => {
    const nombre = formData.name.trim()
    errors.name = []
    
    if (!nombre) {
      errors.name.push('El nombre del paciente es obligatorio')
      return false
    }
    
    if (nombre.length < 2) {
      errors.name.push('El nombre debe tener al menos 2 caracteres')
      return false
    }
    
    const palabras = nombre.split(/\s+/).filter(p => p.length > 0)
    if (palabras.length < 2) {
      errors.name.push('Ingrese el nombre completo (nombre y apellido)')
      return false
    }
    
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/.test(nombre)) {
      errors.name.push('El nombre solo puede contener letras, espacios, guiones y apostrofes')
      return false
    }

    return true
  }

  const validateEdad = (): boolean => {
    const edad = parseInt(formData.age as string)
    errors.age = []
    warnings.age = []
    
    if (!formData.age || isNaN(edad)) {
      errors.age.push('La edad es obligatoria')
      return false
    }
    
    if (edad < 0) {
      errors.age.push('La edad no puede ser negativa')
      return false
    }
    
    if (edad > 150) {
      errors.age.push('La edad no puede ser mayor a 150 años')
      return false
    }
    
    if (edad > 120) warnings.age.push('Edad muy alta, verifique que sea correcta')
    else if (edad === 0) warnings.age.push('¿Es un recién nacido? Considere usar meses si es menor a 1 año')

    return true
  }

  const validateRequiredFields = (): boolean => {
    const requiredFields = ['gender', 'entity', 'careType']
    return requiredFields.every(field => formData[field as keyof PatientData])
  }

  const validateForm = (): boolean => {
    validationState.hasAttemptedSubmit = true
    return validateCedula() && validateNombre() && validateEdad() && validateRequiredFields()
  }

  const handleCedulaInput = (value: string): void => {
    const numericValue = value.replace(/\D/g, '')
    formData.patientCode = numericValue
    
    if (numericValue.length > 0) validateCedula()
    else { errors.patientCode = []; warnings.patientCode = [] }
  }

  const handleNombreInput = (value: string): void => {
    // Solo permitir letras, espacios, guiones y apostrofes
    const lettersOnly = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']/g, '')
    const capitalizedValue = lettersOnly.replace(/\b\w/g, (char) => char.toUpperCase())
    formData.name = capitalizedValue
    
    if (capitalizedValue.length > 0) validateNombre()
    else errors.name = []
  }

  const handleEdadInput = (value: string): void => {
    const numericValue = value.replace(/\D/g, '')
    formData.age = numericValue
    
    if (numericValue.length > 0) validateEdad()
    else { errors.age = []; warnings.age = [] }
  }

  const clearValidationErrors = (): void => {
    Object.keys(errors).forEach(key => errors[key as keyof PatientFormErrors] = [])
    Object.keys(warnings).forEach(key => warnings[key as keyof PatientFormWarnings] = [])
  }

  const clearValidationState = (): void => {
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
    validationState.isValidating = false
  }

  const clearForm = (): void => {
    Object.keys(formData).forEach(key => formData[key as keyof PatientData] = '')
    clearValidationErrors()
    clearValidationState()
  }


  return {
    formData, validationState, errors, warnings, isLoading, validateForm,
    handleCedulaInput, handleNombreInput, handleEdadInput, clearForm
  }
}
