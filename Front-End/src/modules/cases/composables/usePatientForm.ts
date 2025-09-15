import { ref, reactive } from 'vue'
import type { PatientData, PatientFormErrors, PatientFormWarnings, ValidationState } from '../types'

export function usePatientForm() {
  const formData = reactive<PatientData>({
    pacienteCode: '', nombrePaciente: '', sexo: '', edad: '', entidad: '', tipoAtencion: '', observaciones: ''
  })

  const validationState = reactive<ValidationState>({
    hasAttemptedSubmit: false, isValidating: false, showValidationError: false
  })

  const errors = reactive<PatientFormErrors>({ pacienteCode: [], nombrePaciente: [], edad: [] })
  const warnings = reactive<PatientFormWarnings>({ pacienteCode: [], edad: [] })
  const isLoading = ref(false)

  const validateCedula = (): boolean => {
    const cedula = formData.pacienteCode.trim()
    errors.pacienteCode = []
    warnings.pacienteCode = []

    if (!cedula) {
      if (validationState.hasAttemptedSubmit) errors.pacienteCode.push('La cédula es obligatoria')
      return false
    }

    if (!/^\d+$/.test(cedula)) {
      errors.pacienteCode.push('La cédula debe contener solo números')
      return false
    }

    if (cedula.length > 10) {
      errors.pacienteCode.push('La cédula no puede tener más de 10 dígitos')
      return false
    }

    if (cedula.length > 0 && cedula.length < 6) {
      const faltan = 6 - cedula.length
      warnings.pacienteCode.push(`Faltan ${faltan} dígito${faltan === 1 ? '' : 's'} para una cédula válida`)
      
      if (validationState.hasAttemptedSubmit) {
        errors.pacienteCode.push('La cédula debe tener al menos 6 dígitos')
        warnings.pacienteCode = []
        return false
      }
    }

    return true
  }

  const validateNombre = (): boolean => {
    const nombre = formData.nombrePaciente.trim()
    errors.nombrePaciente = []
    
    if (!nombre) {
      errors.nombrePaciente.push('El nombre del paciente es obligatorio')
      return false
    }
    
    if (nombre.length < 2) {
      errors.nombrePaciente.push('El nombre debe tener al menos 2 caracteres')
      return false
    }
    
    const palabras = nombre.split(/\s+/).filter(p => p.length > 0)
    if (palabras.length < 2) {
      errors.nombrePaciente.push('Ingrese el nombre completo (nombre y apellido)')
      return false
    }
    
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/.test(nombre)) {
      errors.nombrePaciente.push('El nombre solo puede contener letras, espacios, guiones y apostrofes')
      return false
    }

    return true
  }

  const validateEdad = (): boolean => {
    const edad = parseInt(formData.edad as string)
    errors.edad = []
    warnings.edad = []
    
    if (!formData.edad || isNaN(edad)) {
      errors.edad.push('La edad es obligatoria')
      return false
    }
    
    if (edad < 0) {
      errors.edad.push('La edad no puede ser negativa')
      return false
    }
    
    if (edad > 150) {
      errors.edad.push('La edad no puede ser mayor a 150 años')
      return false
    }
    
    if (edad > 120) warnings.edad.push('Edad muy alta, verifique que sea correcta')
    else if (edad === 0) warnings.edad.push('¿Es un recién nacido? Considere usar meses si es menor a 1 año')

    return true
  }

  const validateRequiredFields = (): boolean => {
    const requiredFields = ['sexo', 'entidad', 'tipoAtencion']
    return requiredFields.every(field => formData[field as keyof PatientData])
  }

  const validateForm = (): boolean => {
    validationState.hasAttemptedSubmit = true
    return validateCedula() && validateNombre() && validateEdad() && validateRequiredFields()
  }

  const handleCedulaInput = (value: string): void => {
    const numericValue = value.replace(/\D/g, '')
    formData.pacienteCode = numericValue
    
    if (numericValue.length > 0) validateCedula()
    else { errors.pacienteCode = []; warnings.pacienteCode = [] }
  }

  const handleNombreInput = (value: string): void => {
    // Solo permitir letras, espacios, guiones y apostrofes
    const lettersOnly = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']/g, '')
    const capitalizedValue = lettersOnly.replace(/\b\w/g, (char) => char.toUpperCase())
    formData.nombrePaciente = capitalizedValue
    
    if (capitalizedValue.length > 0) validateNombre()
    else errors.nombrePaciente = []
  }

  const handleEdadInput = (value: string): void => {
    const numericValue = value.replace(/\D/g, '')
    formData.edad = numericValue
    
    if (numericValue.length > 0) validateEdad()
    else { errors.edad = []; warnings.edad = [] }
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
