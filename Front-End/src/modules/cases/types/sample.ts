export interface FormTestInfo {
  code: string
  cantidad: number
  nombre?: string
}

export interface FormSubSample {
  numero: number
  regionCuerpo: string
  pruebas: FormTestInfo[]
}

export interface CaseFormData {
  pacienteCedula: string
  fechaIngreso: string
  medicoSolicitante: string
  servicio: string
  entidadPaciente: string
  tipoAtencionPaciente: string
  prioridadCaso: string
  numeroMuestras: string
  muestras: FormSubSample[]
  observaciones: string
}

export interface CaseFormDefaults {
  fechaIngreso: string
  medicoSolicitante: string
  servicio: string
  entidadPaciente: string
  tipoAtencionPaciente: string
  prioridadCaso: string
  numeroMuestras: string
  muestras: FormSubSample[]
  observaciones: string
}

export interface CaseValidationState {
  hasAttemptedSubmit: boolean
  showValidationError: boolean
  isValidating: boolean
}

export interface CaseFormErrors {
  fechaIngreso: string[]
  medicoSolicitante: string[]
  servicio: string[]
  entidadPaciente: string[]
  tipoAtencionPaciente: string[]
  prioridadCaso: string[]
  numeroMuestras: string[]
  muestras: string[]
  observaciones: string[]
}

export interface CaseFormWarnings {
  fechaIngreso: string[]
  medicoSolicitante: string[]
  servicio: string[]
  prioridadCaso: string[]
  numeroMuestras: string[]
}

export interface CaseCreationResult {
  success: boolean
  case?: CreatedCase
  message?: string
  codigo?: string
}

export interface CreatedCase {
  id: string
  codigo: string
  paciente: {
    paciente_code?: string
    cedula?: string  // Mantener por compatibilidad
    nombre: string
    edad: number
    sexo: string
    entidad: string
    tipoAtencion: string
  }
  fechaIngreso: string
  medicoSolicitante: string
  servicio: string
  prioridad: string
  muestras: FormSubSample[]
  observaciones: string
  estado: string
  fechaCreacion: string
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
  { value: 'Prioritario', label: 'Prioritario' },
  { value: 'Urgente', label: 'Urgente' }
]
