/**
 * Tipos específicos para la gestión de residentes en el módulo profile
 */

/**
 * Modelo del formulario de creación de residentes
 */
export interface ResidentFormModel {
  residenteName: string
  InicialesResidente: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  password: string
  observaciones: string
  isActive: boolean
}

/**
 * Request para crear un nuevo residente (colección residentes)
 */
export interface ResidentCreateRequest {
  residente_name: string
  iniciales_residente: string
  residente_code: string
  residente_email: string
  registro_medico: string
  password: string // Contraseña para crear el usuario asociado
  observaciones: string
  is_active: boolean
}

/**
 * Response de creación de residente
 */
export interface ResidentCreateResponse {
  id: string
  residente_name: string
  iniciales_residente: string
  residente_code: string
  residente_email: string
  registro_medico: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion?: string
}

/**
 * Estado de la operación de creación
 */
export interface ResidentCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario
 */
export interface ResidentFormValidation {
  isValid: boolean
  errors: {
    residenteName?: string
    InicialesResidente?: string
    residenteCode?: string
    ResidenteEmail?: string
    registro_medico?: string
    password?: string
    observaciones?: string
  }
}

/**
 * Modelo del formulario de edición de residentes
 */
export interface ResidentEditFormModel {
  id: string
  residenteName: string
  InicialesResidente: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  observaciones: string
  isActive: boolean
  password?: string
}

/**
 * Request para actualizar un residente
 */
export interface ResidentUpdateRequest {
  residente_name: string
  iniciales_residente: string
  residente_email: string
  registro_medico: string
  observaciones: string
  is_active: boolean
  password?: string
}

/**
 * Response de actualización de residente
 */
export interface ResidentUpdateResponse {
  id: string
  residenteName: string
  InicialesResidente: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  observaciones: string
  isActive: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}

/**
 * Estado de la edición de residentes
 */
export interface ResidentEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario de edición
 */
export interface ResidentEditFormValidation {
  isValid: boolean
  errors: {
    residenteName?: string
    InicialesResidente?: string
    residenteCode?: string
    ResidenteEmail?: string
    registro_medico?: string
    observaciones?: string
  }
}
