// Case form state/validation composable: holds reactive form, validations and helpers
import { ref, reactive, computed } from 'vue'
import type { 
  CaseValidationState, FormSubSample, FormTestInfo
} from '../types/sample'
import { MAX_MUESTRAS } from '../types/sample'

// Definir tipos locales para evitar conflictos
interface LocalCaseFormData {
  patientDocument: string
  entryDate: string
  requestingPhysician: string
  service: string
  patientEntity: string
  patientCareType: string
  casePriority: string
  numberOfSamples: string
  samples: FormSubSample[]
  observations: string
}

interface LocalCaseFormErrors {
  entryDate: string[]
  requestingPhysician: string[]
  service: string[]
  patientEntity: string[]
  patientCareType: string[]
  casePriority: string[]
  numberOfSamples: string[]
  samples: string[]
  observations: string[]
}

interface LocalCaseFormWarnings {
  entryDate: string[]
  requestingPhysician: string[]
  service: string[]
  casePriority: string[]
  numberOfSamples: string[]
}

export function useCaseForm() {
  const formData = reactive<LocalCaseFormData>({
    patientDocument: '',
    entryDate: new Date().toISOString().split('T')[0],
    requestingPhysician: '',
    service: '',
    patientEntity: '',
    patientCareType: '',
    casePriority: '',
    numberOfSamples: '1',
    samples: [{ number: 1, bodyRegion: '', tests: [{ code: '', quantity: 1, name: '' }] }],
    observations: ''
  })

  // UI validation flags
  const validationState = reactive<CaseValidationState>({ hasAttemptedSubmit: false, showValidationError: false, isValidating: false })

  // Validation messages
  const errors = reactive<LocalCaseFormErrors>({ entryDate: [], requestingPhysician: [], service: [], patientEntity: [], patientCareType: [], casePriority: [], numberOfSamples: [], samples: [], observations: [] })

  const warnings = reactive<LocalCaseFormWarnings>({ entryDate: [], requestingPhysician: [], service: [], casePriority: [], numberOfSamples: [] })

  const isLoading = ref(false)

  // Factories
  const createEmptySubSample = (number: number): FormSubSample => ({ 
    number: number, 
    bodyRegion: '', 
    tests: [{ code: '', quantity: 1, name: '' }] 
  })

  const createEmptyTest = (): FormTestInfo => ({ code: '', quantity: 1, name: '' })

  // Field validations
  const validateEntryDate = (): boolean => {
    errors.entryDate = []
    warnings.entryDate = []

    if (!formData.entryDate) {
      errors.entryDate.push('La fecha de ingreso es obligatoria')
      return false
    }

    const entryDate = new Date(formData.entryDate)
    const today = new Date()
    
    if (entryDate > today) {
      errors.entryDate.push('La fecha de ingreso no puede ser futura')
      return false
    }

    const daysDifference = Math.ceil((today.getTime() - entryDate.getTime()) / (1000 * 3600 * 24))
    if (daysDifference > 30) {
      warnings.entryDate.push('La fecha de ingreso es muy antigua (más de 30 días)')
    }

    return true
  }

  const validateRequestingPhysician = (): boolean => {
    errors.requestingPhysician = []
    warnings.requestingPhysician = []

    if (!formData.requestingPhysician?.trim()) {
      errors.requestingPhysician.push('El médico solicitante es requerido')
      return false
    }

    if (formData.requestingPhysician.trim().length < 3) {
      errors.requestingPhysician.push('El nombre del médico debe tener al menos 3 caracteres')
      return false
    }

    return true
  }

  const validateService = (): boolean => {
    errors.service = []
    warnings.service = []

    if (formData.requestingPhysician?.trim()) {
      const sv = formData.service?.trim() || ''
      if (!sv) { errors.service.push('El servicio es requerido cuando se especifica un médico'); return false }
      if (sv.length < 2) { errors.service.push('El servicio debe tener al menos 2 caracteres'); return false }
    }

    return true
  }

  const validatePriority = (): boolean => {
    errors.casePriority = []
    warnings.casePriority = []

    if (!formData.casePriority) {
      errors.casePriority.push('La prioridad del caso es requerida')
      return false
    }

    if (!['Normal', 'Prioritario'].includes(formData.casePriority)) {
      errors.casePriority.push('La prioridad seleccionada no es válida')
      return false
    }

    return true
  }

  const validateNumberOfSamples = (): boolean => {
    errors.numberOfSamples = []
    warnings.numberOfSamples = []

    const number = parseInt(formData.numberOfSamples)
    
    if (isNaN(number) || number < 1) {
      errors.numberOfSamples.push('Debe especificar al menos 1 muestra')
      return false
    }

    if (number > MAX_MUESTRAS) {
      errors.numberOfSamples.push(`No se pueden crear más de ${MAX_MUESTRAS} muestras`)
      return false
    }

    if (number > 5) {
      warnings.numberOfSamples.push('Número alto de muestras, verifique que sea correcto')
    }

    return true
  }

  const validateSamples = (): boolean => {
    errors.samples = []

    if (formData.samples.length === 0) {
      errors.samples.push('Debe tener al menos una muestra')
      return false
    }

    let hasErrors = false

    formData.samples.forEach((sample, index) => {
      if (!sample.bodyRegion.trim()) {
        errors.samples.push(`Muestra ${index + 1}: La región del cuerpo es obligatoria`)
        hasErrors = true
      }

      if (sample.tests.length === 0) {
        errors.samples.push(`Muestra ${index + 1}: Debe tener al menos una prueba`)
        hasErrors = true
      } else {
        sample.tests.forEach((test, tIndex) => {
          if (test.code.trim() === '') {
            errors.samples.push(`Muestra ${index + 1}, Prueba ${tIndex + 1}: El código de la prueba es obligatorio`)
            hasErrors = true
          }
        })
      }
    })

    return !hasErrors
  }

  const validateRequiredFields = (): boolean => {
    const requiredFields = ['patientEntity', 'patientCareType', 'entryDate', 'casePriority', 'requestingPhysician']
    
    const basicFieldsValid = requiredFields.every(field => 
      formData[field as keyof LocalCaseFormData] && 
      String(formData[field as keyof LocalCaseFormData]).trim() !== ''
    )
    
    const serviceValid = !formData.requestingPhysician?.trim() || !!(formData.service?.trim())
    
    return basicFieldsValid && serviceValid
  }

  const validateForm = (): boolean => {
    validationState.hasAttemptedSubmit = true
    return validateEntryDate() && validateRequestingPhysician() && validateService() && validatePriority() &&
           validateNumberOfSamples() && validateSamples() && validateRequiredFields()
  }

  // Add/remove sub-samples to match the selected count
  const handleNumberOfSamplesChange = (newNumber: string): void => {
    const number = parseInt(newNumber)
    if (isNaN(number) || number < 1) return
    
    formData.numberOfSamples = newNumber
    
    if (number > formData.samples.length) {
      while (formData.samples.length < number) formData.samples.push(createEmptySubSample(formData.samples.length + 1))
    } else if (number < formData.samples.length) {
      formData.samples = formData.samples.slice(0, number)
    }
  }

  const addTestToSample = (sampleIndex: number): void => { 
    if (sampleIndex >= 0 && sampleIndex < formData.samples.length) 
      formData.samples[sampleIndex].tests.push(createEmptyTest()) 
  }

  const removeTestFromSample = (sampleIndex: number, testIndex: number): void => {
    if (sampleIndex < 0 || sampleIndex >= formData.samples.length) return
    const sample = formData.samples[sampleIndex]
    if (sample.tests.length > 1 && testIndex >= 0 && testIndex < sample.tests.length) 
      sample.tests.splice(testIndex, 1)
  }

  // Reset validation messages/flags
  const clearValidationErrors = (): void => {
    Object.keys(errors).forEach(key => (errors[key as keyof LocalCaseFormErrors] = []))
    Object.keys(warnings).forEach(key => (warnings[key as keyof LocalCaseFormWarnings] = []))
  }

  const clearValidationState = (): void => { validationState.hasAttemptedSubmit = false; validationState.showValidationError = false; validationState.isValidating = false }

  // Reset form to pristine state
  const clearForm = (): void => {
    Object.assign(formData, {
      patientDocument: '',
      entryDate: new Date().toISOString().split('T')[0],
      requestingPhysician: '',
      service: '',
      patientEntity: '',
      patientCareType: '',
      casePriority: '',
      numberOfSamples: '1',
      samples: [{ number: 1, bodyRegion: '', tests: [{ code: '', quantity: 1, name: '' }] }],
      observations: ''
    })
    
    clearValidationState()
    clearValidationErrors()
  }

  const isFormValid = computed(() => (
    formData.patientEntity && formData.patientCareType && formData.entryDate && formData.casePriority && formData.requestingPhysician && formData.numberOfSamples &&
    (!formData.requestingPhysician.trim() || formData.service.trim()) &&
    formData.samples.length > 0 && formData.samples.every(sample => sample.bodyRegion.trim() !== '' && sample.tests.some(test => test.code.trim() !== ''))
  ))

  return {
    formData, validationState, errors, warnings, isLoading, isFormValid,
    validateForm, clearForm, handleNumberOfSamplesChange, addTestToSample,
    removeTestFromSample, createEmptySubSample, createEmptyTest
  }
}