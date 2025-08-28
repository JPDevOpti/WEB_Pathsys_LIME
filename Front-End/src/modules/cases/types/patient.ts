export interface PatientData {
  pacienteCode: string
  nombrePaciente: string
  sexo: 'masculino' | 'femenino' | ''
  edad: string
  entidad: string
  entidadCodigo?: string
  tipoAtencion: 'ambulatorio' | 'hospitalizado' | ''
  observaciones: string
  codigo?: string
}

export interface PatientFormErrors {
  pacienteCode: string[]
  nombrePaciente: string[]
  edad: string[]
}

export interface PatientFormWarnings {
  pacienteCode: string[]
  edad: string[]
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
