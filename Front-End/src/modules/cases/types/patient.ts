// ============================================================================
// INTERFACES DE DATOS DE PACIENTE
// ============================================================================

/**
 * Datos del paciente para formularios
 */
export interface PatientData {
  numeroCedula: string
  nombrePaciente: string
  sexo: 'masculino' | 'femenino' | ''
  edad: string
  entidad: string
  entidadCodigo?: string
  tipoAtencion: 'ambulatorio' | 'hospitalizado' | ''
  observaciones: string
  codigo?: string
}

// ============================================================================
// INTERFACES DE VALIDACIÓN
// ============================================================================

/**
 * Errores de validación del formulario de paciente
 */
export interface PatientFormErrors {
  numeroCedula: string[]
  nombrePaciente: string[]
  edad: string[]
}

/**
 * Advertencias del formulario de paciente
 */
export interface PatientFormWarnings {
  numeroCedula: string[]
  edad: string[]
}

/**
 * Estado de validación del formulario
 */
export interface ValidationState {
  hasAttemptedSubmit: boolean
  isValidating: boolean
  showValidationError: boolean
}

// ============================================================================
// INTERFACES DE NOTIFICACIONES
// ============================================================================

/**
 * Estado de notificación del sistema
 */
export interface NotificationState {
  visible: boolean
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
}
