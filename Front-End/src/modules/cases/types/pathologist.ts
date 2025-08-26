// ============================================================================
// INTERFACES DE INFORMACIÓN DE PATÓLOGOS
// ============================================================================

/**
 * Información básica de un patólogo (para formularios)
 */
export interface FormPathologistInfo {
  id: string
  nombre: string
  iniciales?: string
  documento: string
  email: string
  medicalLicense: string
  isActive: boolean
}

// ============================================================================
// INTERFACES DE ASIGNACIÓN
// ============================================================================

/**
 * Datos para asignar patólogo a un caso
 */
export interface PathologistAssignmentData {
  caseId: string
  pathologistId: string
  fechaAsignacion: string
  observaciones?: string
}

/**
 * Estado de asignación de patólogo
 */
export interface PathologistAssignmentState {
  isAssigned: boolean
  assignedDate?: string
  pathologist?: FormPathologistInfo
}

/**
 * Formulario de asignación de patólogo
 */
export interface PathologistFormData {
  patologoId: string
  fechaAsignacion: string
}

// ============================================================================
// INTERFACES DE VALIDACIÓN Y RESULTADOS
// ============================================================================

/**
 * Errores de validación para patólogo
 */
export interface PathologistFormErrors {
  patologoId: string[]
  fechaAsignacion: string[]
}

/**
 * Resultado de asignación de patólogo
 */
export interface PathologistAssignmentResult {
  success: boolean
  assignment?: PathologistAssignmentState
  message?: string
}
