// ============================================================================
// INTERFACES DE PRUEBAS Y MUESTRAS
// ============================================================================

/**
 * Información de una prueba médica con cantidad (para formularios)
 */
export interface FormTestInfo {
  code: string
  cantidad: number
  nombre?: string
}

/**
 * Información de una submuestra (para formularios)
 */
export interface FormSubSample {
  numero: number
  regionCuerpo: string
  pruebas: FormTestInfo[]
}

// ============================================================================
// INTERFACES DE FORMULARIOS
// ============================================================================

/**
 * Datos del formulario de muestra/caso
 */
export interface CaseFormData {
  // Información del paciente (referencia)
  pacienteCedula: string
  
  // Datos del caso
  fechaIngreso: string
  medicoSolicitante: string
  servicio: string
  entidadPaciente: string
  tipoAtencionPaciente: string
  numeroMuestras: string
  
  // Submuestras
  muestras: FormSubSample[]
  
  // Observaciones
  observaciones: string
}

/**
 * Datos iniciales para el formulario de caso
 */
export interface CaseFormDefaults {
  fechaIngreso: string
  medicoSolicitante: string
  servicio: string
  entidadPaciente: string
  tipoAtencionPaciente: string
  numeroMuestras: string
  muestras: FormSubSample[]
  observaciones: string
}

// ============================================================================
// INTERFACES DE VALIDACIÓN
// ============================================================================

/**
 * Estado de validación del formulario de caso
 */
export interface CaseValidationState {
  hasAttemptedSubmit: boolean
  showValidationError: boolean
  isValidating: boolean
}

/**
 * Errores de validación del formulario de caso
 */
export interface CaseFormErrors {
  fechaIngreso: string[]
  medicoSolicitante: string[]
  servicio: string[]
  entidadPaciente: string[]
  tipoAtencionPaciente: string[]
  numeroMuestras: string[]
  muestras: string[]
  observaciones: string[]
}

/**
 * Advertencias del formulario de caso
 */
export interface CaseFormWarnings {
  fechaIngreso: string[]
  medicoSolicitante: string[]
  servicio: string[]
  numeroMuestras: string[]
}

// ============================================================================
// INTERFACES DE RESULTADOS
// ============================================================================

/**
 * Resultado de la creación de un caso
 */
export interface CaseCreationResult {
  success: boolean
  case?: CreatedCase
  message?: string
  codigo?: string
}

/**
 * Tipo para el caso creado en la notificación
 */
export interface CreatedCase {
  id: string
  codigo: string
  paciente: {
    cedula: string
    nombre: string
    edad: number
    sexo: string
    entidad: string
    tipoAtencion: string
  }
  fechaIngreso: string
  medicoSolicitante: string
  servicio: string
  muestras: FormSubSample[]
  observaciones: string
  estado: string
  fechaCreacion: string
}

// ============================================================================
// INTERFACES DE OPCIONES Y CONFIGURACIÓN
// ============================================================================

/**
 * Opciones para selectores
 */
export interface SelectOption {
  value: string
  label: string
}

/**
 * Configuración máxima de muestras
 */
export const MAX_MUESTRAS = 10

/**
 * Tipos de atención disponibles
 */
export const TIPOS_ATENCION: SelectOption[] = [
  { value: 'ambulatorio', label: 'Ambulatorio' },
  { value: 'hospitalizado', label: 'Hospitalizado' }
]
