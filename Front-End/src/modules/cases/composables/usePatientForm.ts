import { ref, reactive, computed } from 'vue'
import type { PatientData, PatientFormErrors, PatientFormWarnings, ValidationState } from '../types'

export function usePatientForm() {
  // ============================================================================
  // ESTADO DEL FORMULARIO
  // ============================================================================
  
  const formData = reactive<PatientData>({
    pacienteCode: '',
    nombrePaciente: '',
    sexo: '',
    edad: '',
    entidad: '',
    tipoAtencion: '',
    observaciones: ''
  })

  // ============================================================================
  // ESTADO DE VALIDACIÓN
  // ============================================================================
  
  const validationState = reactive<ValidationState>({
    hasAttemptedSubmit: false,
    isValidating: false,
    showValidationError: false
  })

  const errors = reactive<PatientFormErrors>({
    pacienteCode: [],
    nombrePaciente: [],
    edad: []
  })

  const warnings = reactive<PatientFormWarnings>({
    pacienteCode: [],
    edad: []
  })

  const isLoading = ref(false)

  // ============================================================================
  // FUNCIONES DE VALIDACIÓN
  // ============================================================================

  /**
   * Valida el campo de cédula
   * @returns true si la cédula es válida
   */
  const validateCedula = (): boolean => {
    const cedula = formData.pacienteCode.trim()
    errors.pacienteCode = []
    warnings.pacienteCode = []

    if (!cedula) {
      if (validationState.hasAttemptedSubmit) {
        errors.pacienteCode.push('La cédula es obligatoria')
      }
      return false
    }

    // Validar solo números
    if (!/^\d+$/.test(cedula)) {
      errors.pacienteCode.push('La cédula debe contener solo números')
      return false
    }

    // Validar longitud máxima
    if (cedula.length > 10) {
      errors.pacienteCode.push('La cédula no puede tener más de 10 dígitos')
      return false
    }

    // Mensaje reactivo: cuántos dígitos faltan para ser válida (mínimo 6)
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

  /**
   * Valida el campo de nombre
   * @returns true si el nombre es válido
   */
  const validateNombre = (): boolean => {
    const nombre = formData.nombrePaciente.trim()
    errors.nombrePaciente = []
    
    if (!nombre) {
      if (validationState.hasAttemptedSubmit) {
        errors.nombrePaciente.push('El nombre del paciente es obligatorio')
      }
      return false
    }
    
    // Validar longitud mínima
    if (nombre.length < 2) {
      errors.nombrePaciente.push('El nombre debe tener al menos 2 caracteres')
      return false
    }
    
    // Validar que contenga al menos dos palabras
    const palabras = nombre.split(/\s+/).filter(p => p.length > 0)
    if (palabras.length < 2) {
      errors.nombrePaciente.push('Ingrese el nombre completo (nombre y apellido)')
      return false
    }
    
    // Validar caracteres válidos (letras, espacios, acentos, guiones)
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/.test(nombre)) {
      errors.nombrePaciente.push('El nombre solo puede contener letras, espacios, guiones y apostrofes')
      return false
    }

    return true
  }

  /**
   * Valida el campo de edad
   * @returns true si la edad es válida
   */
  const validateEdad = (): boolean => {
    const edad = parseInt(formData.edad as string)
    errors.edad = []
    warnings.edad = []
    
    if (!formData.edad || isNaN(edad)) {
      if (validationState.hasAttemptedSubmit) {
        errors.edad.push('La edad es obligatoria')
      }
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
    
    // Advertencias
    if (edad > 120) {
      warnings.edad.push('Edad muy alta, verifique que sea correcta')
    } else if (edad === 0) {
      warnings.edad.push('¿Es un recién nacido? Considere usar meses si es menor a 1 año')
    }

    return true
  }

  /**
   * Valida todos los campos requeridos
   * @returns true si todos los campos requeridos están completos
   */
  const validateRequiredFields = (): boolean => {
    const requiredFields = ['sexo', 'entidad', 'tipoAtencion']
    return requiredFields.every(field => formData[field as keyof PatientData])
  }

  /**
   * Ejecuta la validación completa del formulario
   * @returns true si el formulario es válido
   */
  const validateForm = (): boolean => {
    validationState.hasAttemptedSubmit = true
    
    const isCedulaValid = validateCedula()
    const isNombreValid = validateNombre()
    const isEdadValid = validateEdad()
    const hasRequiredFields = validateRequiredFields()
    
    return isCedulaValid && isNombreValid && isEdadValid && hasRequiredFields
  }

  // ============================================================================
  // FUNCIONES DE MANIPULACIÓN DE INPUT
  // ============================================================================

  /**
   * Maneja el input de cédula, permitiendo solo números
   * @param value - Valor ingresado
   */
  const handleCedulaInput = (value: string): void => {
    // Solo permitir números
    const numericValue = value.replace(/\D/g, '')
    formData.pacienteCode = numericValue
    
    // Validar en tiempo real
    if (numericValue.length > 0) {
      validateCedula()
    } else {
      errors.pacienteCode = []
      warnings.pacienteCode = []
    }
  }

  /**
   * Maneja el input de nombre, capitalizando palabras
   * @param value - Valor ingresado
   */
  const handleNombreInput = (value: string): void => {
    // Capitalizar primera letra de cada palabra
    const capitalizedValue = value.replace(/\b\w/g, (char) => char.toUpperCase())
    formData.nombrePaciente = capitalizedValue
    
    // Validar en tiempo real
    if (capitalizedValue.length > 0) {
      validateNombre()
    } else {
      errors.nombrePaciente = []
    }
  }

  /**
   * Maneja el input de edad, permitiendo solo números
   * @param value - Valor ingresado
   */
  const handleEdadInput = (value: string): void => {
    // Solo permitir números
    const numericValue = value.replace(/\D/g, '')
    formData.edad = numericValue
    
    // Validar en tiempo real
    if (numericValue.length > 0) {
      validateEdad()
    } else {
      errors.edad = []
      warnings.edad = []
    }
  }

  // ============================================================================
  // FUNCIONES DE LIMPIEZA
  // ============================================================================

  /**
   * Limpia todos los errores y advertencias
   */
  const clearValidationErrors = (): void => {
    Object.keys(errors).forEach(key => {
      errors[key as keyof PatientFormErrors] = []
    })
    Object.keys(warnings).forEach(key => {
      warnings[key as keyof PatientFormWarnings] = []
    })
  }

  /**
   * Limpia el estado de validación
   */
  const clearValidationState = (): void => {
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
    validationState.isValidating = false
  }

  /**
   * Limpia completamente el formulario
   */
  const clearForm = (): void => {
    Object.keys(formData).forEach(key => {
      formData[key as keyof PatientData] = ''
    })
    
    clearValidationErrors()
    clearValidationState()
  }

  // ============================================================================
  // COMPUTED PROPERTIES
  // ============================================================================

  /**
   * Clases CSS para el campo de cédula
   */
  const getCedulaFieldClasses = computed(() => {
    const baseClasses = "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
    
    if (errors.pacienteCode.length > 0) {
      return `${baseClasses} border-red-500 bg-red-50`
    }
    
    if (warnings.pacienteCode.length > 0) {
      return `${baseClasses} border-yellow-500 bg-yellow-50`
    }
    
    if (formData.pacienteCode && errors.pacienteCode.length === 0) {
      return `${baseClasses} border-green-500 bg-green-50`
    }
    
    return `${baseClasses} border-gray-300`
  })

  /**
   * Clases CSS para el campo de nombre
   */
  const getNombreFieldClasses = computed(() => {
    const baseClasses = "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
    
    if (errors.nombrePaciente.length > 0) {
      return `${baseClasses} border-red-500 bg-red-50`
    }
    
    if (formData.nombrePaciente && errors.nombrePaciente.length === 0) {
      return `${baseClasses} border-green-500 bg-green-50`
    }
    
    return `${baseClasses} border-gray-300`
  })

  /**
   * Clases CSS para el campo de edad
   */
  const getEdadFieldClasses = computed(() => {
    const baseClasses = "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
    
    if (errors.edad.length > 0) {
      return `${baseClasses} border-red-500 bg-red-50`
    }
    
    if (warnings.edad.length > 0) {
      return `${baseClasses} border-yellow-500 bg-yellow-50`
    }
    
    if (formData.edad && errors.edad.length === 0) {
      return `${baseClasses} border-green-500 bg-green-50`
    }
    
    return `${baseClasses} border-gray-300`
  })

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado
    formData,
    validationState,
    errors,
    warnings,
    isLoading,
    
    // Funciones de validación
    validateForm,
    validateCedula,
    validateNombre,
    validateEdad,
    
    // Handlers de input
    handleCedulaInput,
    handleNombreInput,
    handleEdadInput,
    
    // Utilidades
    clearForm,
    
    // Computed classes
    getCedulaFieldClasses,
    getNombreFieldClasses,
    getEdadFieldClasses
  }
}
