import { ref, reactive, computed } from 'vue'
import type { 
  CaseFormData, 
  CaseFormErrors, 
  CaseFormWarnings, 
  CaseValidationState,
  FormSubSample,
  FormTestInfo
} from '../types'
import { MAX_MUESTRAS } from '../types'

export function useCaseForm() {
  const formData = reactive<CaseFormData>({
    pacienteCedula: '',
    fechaIngreso: new Date().toISOString().split('T')[0],
    medicoSolicitante: '',
    servicio: '',
    entidadPaciente: '',
    tipoAtencionPaciente: '',
    prioridadCaso: '',
    numeroMuestras: '1',
    muestras: [{ numero: 1, regionCuerpo: '', pruebas: [{ code: '', cantidad: 1, nombre: '' }] }],
    observaciones: ''
  })

  const validationState = reactive<CaseValidationState>({
    hasAttemptedSubmit: false,
    showValidationError: false,
    isValidating: false
  })

  const errors = reactive<CaseFormErrors>({
    fechaIngreso: [], medicoSolicitante: [], servicio: [], entidadPaciente: [],
    tipoAtencionPaciente: [], prioridadCaso: [], numeroMuestras: [], muestras: [], observaciones: []
  })

  const warnings = reactive<CaseFormWarnings>({
    fechaIngreso: [], medicoSolicitante: [], servicio: [], prioridadCaso: [], numeroMuestras: []
  })

  const isLoading = ref(false)

  const createEmptySubSample = (numero: number): FormSubSample => ({
    numero, regionCuerpo: '', pruebas: [{ code: '', cantidad: 1, nombre: '' }]
  })

  const createEmptyTest = (): FormTestInfo => ({ code: '', cantidad: 1, nombre: '' })

  const validateFechaIngreso = (): boolean => {
    errors.fechaIngreso = []
    warnings.fechaIngreso = []

    if (!formData.fechaIngreso) {
      errors.fechaIngreso.push('La fecha de ingreso es obligatoria')
      return false
    }

    const fechaIngreso = new Date(formData.fechaIngreso)
    const hoy = new Date()
    
    if (fechaIngreso > hoy) {
      errors.fechaIngreso.push('La fecha de ingreso no puede ser futura')
      return false
    }

    const diferenciaDias = Math.ceil((hoy.getTime() - fechaIngreso.getTime()) / (1000 * 3600 * 24))
    if (diferenciaDias > 30) {
      warnings.fechaIngreso.push('La fecha de ingreso es muy antigua (más de 30 días)')
    }

    return true
  }

  const validateMedicoSolicitante = (): boolean => {
    errors.medicoSolicitante = []
    warnings.medicoSolicitante = []

    if (!formData.medicoSolicitante || !formData.medicoSolicitante.trim()) {
      errors.medicoSolicitante.push('El médico solicitante es requerido')
      return false
    }

    if (formData.medicoSolicitante.trim().length < 3) {
      errors.medicoSolicitante.push('El nombre del médico debe tener al menos 3 caracteres')
      return false
    }

    return true
  }

  const validateServicio = (): boolean => {
    errors.servicio = []
    warnings.servicio = []

    // Solo validar servicio si hay un médico solicitante
    if (formData.medicoSolicitante && formData.medicoSolicitante.trim()) {
      if (!formData.servicio || !formData.servicio.trim()) {
        errors.servicio.push('El servicio es requerido cuando se especifica un médico')
        return false
      }

      if (formData.servicio.trim().length < 2) {
        errors.servicio.push('El servicio debe tener al menos 2 caracteres')
        return false
      }
    }

    return true
  }

  const validatePrioridad = (): boolean => {
    errors.prioridadCaso = []
    warnings.prioridadCaso = []

    if (!formData.prioridadCaso) {
      errors.prioridadCaso.push('La prioridad del caso es requerida')
      return false
    }

    const prioridadesValidas = ['Normal', 'Prioritario', 'Urgente']
    if (!prioridadesValidas.includes(formData.prioridadCaso)) {
      errors.prioridadCaso.push('La prioridad seleccionada no es válida')
      return false
    }

    return true
  }

  const validateNumeroMuestras = (): boolean => {
    errors.numeroMuestras = []
    warnings.numeroMuestras = []

    const numero = parseInt(formData.numeroMuestras)
    
    if (isNaN(numero) || numero < 1) {
      errors.numeroMuestras.push('Debe especificar al menos 1 muestra')
      return false
    }

    if (numero > MAX_MUESTRAS) {
      errors.numeroMuestras.push(`No se pueden crear más de ${MAX_MUESTRAS} muestras`)
      return false
    }

    if (numero > 5) {
      warnings.numeroMuestras.push('Número alto de muestras, verifique que sea correcto')
    }

    return true
  }

  const validateMuestras = (): boolean => {
    errors.muestras = []

    if (formData.muestras.length === 0) {
      errors.muestras.push('Debe tener al menos una muestra')
      return false
    }

    let hasErrors = false

    formData.muestras.forEach((muestra, index) => {
      if (!muestra.regionCuerpo.trim()) {
        errors.muestras.push(`Muestra ${index + 1}: La región del cuerpo es obligatoria`)
        hasErrors = true
      }

      if (muestra.pruebas.length === 0) {
        errors.muestras.push(`Muestra ${index + 1}: Debe tener al menos una prueba`)
        hasErrors = true
      } else {
        const pruebasValidas = muestra.pruebas.filter(prueba => prueba.code.trim() !== '')
        if (pruebasValidas.length === 0) {
          errors.muestras.push(`Muestra ${index + 1}: Debe especificar al menos una prueba`)
          hasErrors = true
        }
      }
    })

    return !hasErrors
  }

  const validateRequiredFields = (): boolean => {
    const requiredFields = [
      'entidadPaciente', 
      'tipoAtencionPaciente', 
      'fechaIngreso', 
      'prioridadCaso', 
      'medicoSolicitante'
    ]
    
    // Validar campos básicos obligatorios
    const basicFieldsValid = requiredFields.every(field => 
      formData[field as keyof CaseFormData] && 
      String(formData[field as keyof CaseFormData]).trim() !== ''
    )
    
    // Validar servicio condicionalmente
    const servicioValid = !formData.medicoSolicitante || 
                         !formData.medicoSolicitante.trim() || 
                         !!(formData.servicio && formData.servicio.trim() !== '')
    
    return basicFieldsValid && servicioValid
  }

  const validateForm = (): boolean => {
    validationState.hasAttemptedSubmit = true
    return validateFechaIngreso() && validateMedicoSolicitante() && validateServicio() && validatePrioridad() &&
           validateNumeroMuestras() && validateMuestras() && validateRequiredFields()
  }

  const handleNumeroMuestrasChange = (nuevoNumero: string): void => {
    const numero = parseInt(nuevoNumero)
    if (isNaN(numero) || numero < 1) return
    
    formData.numeroMuestras = nuevoNumero
    
    if (numero > formData.muestras.length) {
      while (formData.muestras.length < numero) {
        formData.muestras.push(createEmptySubSample(formData.muestras.length + 1))
      }
    } else if (numero < formData.muestras.length) {
      formData.muestras = formData.muestras.slice(0, numero)
    }
  }

  const addPruebaToMuestra = (muestraIndex: number): void => {
    if (muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
      formData.muestras[muestraIndex].pruebas.push(createEmptyTest())
    }
  }

  const removePruebaFromMuestra = (muestraIndex: number, pruebaIndex: number): void => {
    if (muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
      const muestra = formData.muestras[muestraIndex]
      if (muestra.pruebas.length > 1 && pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
        muestra.pruebas.splice(pruebaIndex, 1)
      }
    }
  }

  const clearValidationErrors = (): void => {
    Object.keys(errors).forEach(key => errors[key as keyof CaseFormErrors] = [])
    Object.keys(warnings).forEach(key => warnings[key as keyof CaseFormWarnings] = [])
  }

  const clearValidationState = (): void => {
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
    validationState.isValidating = false
  }

  const clearForm = (): void => {
    Object.assign(formData, {
      pacienteCedula: '',
      fechaIngreso: new Date().toISOString().split('T')[0],
      medicoSolicitante: '',
      servicio: '',
      entidadPaciente: '',
      tipoAtencionPaciente: '',
      prioridadCaso: '',
      numeroMuestras: '1',
      muestras: [{ numero: 1, regionCuerpo: '', pruebas: [{ code: '', cantidad: 1, nombre: '' }] }],
      observaciones: ''
    })
    
    clearValidationState()
    clearValidationErrors()
  }

  const isFormValid = computed(() => {
    // Verificar si los campos están completos sin ejecutar validaciones que modifiquen los errores
    const hasRequiredFields = formData.entidadPaciente && 
                              formData.tipoAtencionPaciente && 
                              formData.fechaIngreso && 
                              formData.prioridadCaso && 
                              formData.medicoSolicitante &&
                              formData.numeroMuestras &&
                              (!formData.medicoSolicitante.trim() || formData.servicio.trim())
    
    const hasMuestrasValid = formData.muestras.length > 0 && 
                           formData.muestras.every(muestra => 
                             muestra.regionCuerpo.trim() !== '' && 
                             muestra.pruebas.some(prueba => prueba.code.trim() !== '')
                           )
    
    return hasRequiredFields && hasMuestrasValid
  })

  return {
    formData, validationState, errors, warnings, isLoading, isFormValid,
    validateForm, clearForm, handleNumeroMuestrasChange, addPruebaToMuestra,
    removePruebaFromMuestra, createEmptySubSample, createEmptyTest,
    validateFechaIngreso, validateMedicoSolicitante, validateServicio, validatePrioridad, validateNumeroMuestras, validateMuestras
  }
}
