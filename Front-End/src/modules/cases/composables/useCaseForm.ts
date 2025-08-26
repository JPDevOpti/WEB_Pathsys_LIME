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
  // ============================================================================
  // ESTADO DEL FORMULARIO
  // ============================================================================

  const formData = reactive<CaseFormData>({
    pacienteCedula: '',
    fechaIngreso: '',
    medicoSolicitante: '',
    servicio: '',
    entidadPaciente: '',
    tipoAtencionPaciente: '',
    numeroMuestras: '1',
    muestras: [createEmptySubSample(1)],
    observaciones: ''
  })

  // ============================================================================
  // ESTADO DE VALIDACIÓN
  // ============================================================================

  const validationState = reactive<CaseValidationState>({
    hasAttemptedSubmit: false,
    showValidationError: false,
    isValidating: false
  })

  const errors = reactive<CaseFormErrors>({
    fechaIngreso: [],
    medicoSolicitante: [],
    servicio: [],
    entidadPaciente: [],
    tipoAtencionPaciente: [],
    numeroMuestras: [],
    muestras: [],
    observaciones: []
  })

  const warnings = reactive<CaseFormWarnings>({
    fechaIngreso: [],
    medicoSolicitante: [],
    servicio: [],
    numeroMuestras: []
  })

  const isLoading = ref(false)

  // ============================================================================
  // FUNCIONES DE CREACIÓN DE DATOS
  // ============================================================================

  /**
   * Crea una submuestra vacía
   * @param numero - Número de la submuestra
   * @returns Submuestra vacía
   */
  function createEmptySubSample(numero: number): FormSubSample {
    return {
      numero,
      regionCuerpo: '',
      pruebas: [{ code: '', cantidad: 1, nombre: '' }]
    }
  }

  /**
   * Crea una prueba vacía
   * @returns Prueba vacía
   */
  function createEmptyTest(): FormTestInfo {
    return {
      code: '',
      cantidad: 1,
      nombre: ''
    }
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Obtiene la fecha actual en formato YYYY-MM-DD
   * @returns Fecha actual formateada
   */
  const getCurrentDate = (): string => {
    const now = new Date()
    return now.toISOString().split('T')[0]
  }

  /**
   * Inicializa el formulario con valores por defecto
   */
  const initializeForm = (): void => {
    formData.fechaIngreso = getCurrentDate()
  }

  // ============================================================================
  // FUNCIONES DE VALIDACIÓN
  // ============================================================================

  /**
   * Valida la fecha de ingreso
   * @returns true si la fecha es válida
   */
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

  /**
   * Valida el médico solicitante
   * @returns true si el médico es válido
   */
  const validateMedicoSolicitante = (): boolean => {
    errors.medicoSolicitante = []
    warnings.medicoSolicitante = []

    if (formData.medicoSolicitante.trim() && formData.medicoSolicitante.trim().length < 3) {
      errors.medicoSolicitante.push('El nombre del médico debe tener al menos 3 caracteres')
      return false
    }

    return true
  }

  /**
   * Valida el número de muestras
   * @returns true si el número es válido
   */
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

  /**
   * Valida las muestras del formulario
   * @returns true si todas las muestras son válidas
   */
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

  /**
   * Valida todos los campos requeridos
   * @returns true si todos los campos requeridos están completos
   */
  const validateRequiredFields = (): boolean => {
    const requiredFields = ['entidadPaciente', 'tipoAtencionPaciente']
    return requiredFields.every(field => 
      formData[field as keyof CaseFormData] && 
      String(formData[field as keyof CaseFormData]).trim() !== ''
    )
  }

  /**
   * Ejecuta la validación completa del formulario
   * @returns true si el formulario es válido
   */
  const validateForm = (): boolean => {
    validationState.hasAttemptedSubmit = true
    
    const isFechaValid = validateFechaIngreso()
    const isMedicoValid = validateMedicoSolicitante()
    const isNumeroValid = validateNumeroMuestras()
    const isMuestrasValid = validateMuestras()
    const hasRequiredFields = validateRequiredFields()
    
    return isFechaValid && isMedicoValid && isNumeroValid && isMuestrasValid && hasRequiredFields
  }

  // ============================================================================
  // FUNCIONES DE MANIPULACIÓN DE MUESTRAS
  // ============================================================================

  /**
   * Maneja el cambio en el número de muestras
   * @param nuevoNumero - Nuevo número de muestras
   */
  const handleNumeroMuestrasChange = (nuevoNumero: string): void => {
    const numero = parseInt(nuevoNumero)
    
    if (isNaN(numero) || numero < 1) return
    
    formData.numeroMuestras = nuevoNumero
    
    // Ajustar array de muestras
    if (numero > formData.muestras.length) {
      // Agregar muestras
      while (formData.muestras.length < numero) {
        formData.muestras.push(createEmptySubSample(formData.muestras.length + 1))
      }
    } else if (numero < formData.muestras.length) {
      // Remover muestras
      formData.muestras = formData.muestras.slice(0, numero)
    }
  }

  /**
   * Agrega una prueba a una muestra específica
   * @param muestraIndex - Índice de la muestra
   */
  const addPruebaToMuestra = (muestraIndex: number): void => {
    if (muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
      formData.muestras[muestraIndex].pruebas.push(createEmptyTest())
    }
  }

  /**
   * Remueve una prueba de una muestra específica
   * @param muestraIndex - Índice de la muestra
   * @param pruebaIndex - Índice de la prueba
   */
  const removePruebaFromMuestra = (muestraIndex: number, pruebaIndex: number): void => {
    if (muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
      const muestra = formData.muestras[muestraIndex]
      if (muestra.pruebas.length > 1 && pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
        muestra.pruebas.splice(pruebaIndex, 1)
      }
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
      errors[key as keyof CaseFormErrors] = []
    })
    Object.keys(warnings).forEach(key => {
      warnings[key as keyof CaseFormWarnings] = []
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
    // Limpiar datos
    formData.pacienteCedula = ''
    formData.fechaIngreso = getCurrentDate()
    formData.medicoSolicitante = ''
    formData.servicio = ''
    formData.entidadPaciente = ''
    formData.tipoAtencionPaciente = ''
    formData.numeroMuestras = '1'
    formData.muestras = [createEmptySubSample(1)]
    formData.observaciones = ''
    
    // Limpiar validación
    clearValidationState()
    clearValidationErrors()
  }

  // ============================================================================
  // COMPUTED PROPERTIES
  // ============================================================================

  /**
   * Verifica si el formulario es válido
   */
  const isFormValid = computed(() => {
    return validateForm()
  })

  // ============================================================================
  // INICIALIZACIÓN
  // ============================================================================

  initializeForm()

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
    
    // Computed
    isFormValid,
    
    // Métodos
    validateForm,
    clearForm,
    handleNumeroMuestrasChange,
    addPruebaToMuestra,
    removePruebaFromMuestra,
    createEmptySubSample,
    createEmptyTest,
    
    // Validaciones individuales
    validateFechaIngreso,
    validateMedicoSolicitante,
    validateNumeroMuestras,
    validateMuestras
  }
}
