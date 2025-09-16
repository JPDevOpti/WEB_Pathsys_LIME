export interface PatientData {
  patientCode: string
  name: string
  gender: 'masculino' | 'femenino' | ''
  age: string
  entity: string
  entityCode?: string
  careType: 'ambulatorio' | 'hospitalizado' | ''
  observations: string
  code?: string
}

export interface PatientFormErrors {
  patientCode: string[]
  name: string[]
  age: string[]
}

export interface PatientFormWarnings {
  patientCode: string[]
  age: string[]
}

export interface ValidationState {
  hasAttemptedSubmit: boolean
  isValidating: boolean
  showValidationError: boolean
}

export interface NotificationState {
  visible: boolean
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
}
