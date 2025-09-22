export interface FormTestInfo {
  code: string
  quantity: number
  name?: string
}

export interface FormSubSample {
  number: number
  bodyRegion: string
  tests: FormTestInfo[]
}

export interface CaseFormData {
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


export interface CaseValidationState {
  hasAttemptedSubmit: boolean
  showValidationError: boolean
  isValidating: boolean
}

export interface CaseFormErrors {
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

export interface CaseFormWarnings {
  entryDate: string[]
  requestingPhysician: string[]
  service: string[]
  casePriority: string[]
  numberOfSamples: string[]
}

export interface CaseCreationResult {
  success: boolean
  case?: CreatedCase
  message?: string
  codigo?: string
}

export interface CreatedCase {
  id: string
  code: string
  patient: {
    patient_code?: string
    cedula?: string  // Mantener por compatibilidad
    name: string
    age: number
    gender: string
    entity: string
    careType: string
  }
  entryDate: string
  requestingPhysician: string
  service: string
  priority: string
  samples: FormSubSample[]
  observations: string
  state: string
  creationDate: string
}

export interface SelectOption {
  value: string
  label: string
}

export const MAX_MUESTRAS = 10

export const TIPOS_ATENCION: SelectOption[] = [
  { value: 'Ambulatorio', label: 'Ambulatorio' },
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

export const PRIORIDADES_CASO: SelectOption[] = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Prioritario', label: 'Prioritario' }
]
