/**
 * Tipos específicos para la gestión de auxiliares en el módulo profile
 */

/**
 * Modelo del formulario de creación de auxiliares
 */
export interface AuxiliaryFormModel {
  auxiliarName: string
  auxiliarCode: string
  AuxiliarEmail: string
  password: string
  observaciones: string
  isActive: boolean
}

/**
 * Request para crear un nuevo auxiliar (colección auxiliares)
 */
export interface AuxiliaryCreateRequest {
  auxiliar_name: string
  auxiliar_code: string
  auxiliar_email: string
  password: string // Contraseña para crear el usuario asociado
  observaciones: string
  is_active: boolean
}

/**
 * Response de creación de auxiliar
 */
export interface AuxiliaryCreateResponse {
  id: string
  auxiliar_name: string
  auxiliar_code: string
  auxiliar_email: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion?: string
}

/**
 * Estado de la operación de creación
 */
export interface AuxiliaryCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario
 */
export interface AuxiliaryFormValidation {
  isValid: boolean
  errors: {
    auxiliarName?: string
    auxiliarCode?: string
    AuxiliarEmail?: string
    password?: string
    observaciones?: string
  }
}

/**
 * Modelo del formulario de edición de auxiliares
 */
export interface AuxiliaryEditFormModel {
  id: string
  auxiliarName: string
  auxiliarCode: string
  AuxiliarEmail: string
  observaciones: string
  isActive: boolean
  password?: string
  passwordConfirm?: string
}

/**
 * Request para actualizar un auxiliar (backend snake_case)
 */
export interface AuxiliaryUpdateRequest {
  auxiliar_name: string
  auxiliar_email: string
  observaciones: string
  is_active: boolean
  password?: string
}

/**
 * Response de actualización de auxiliar (backend snake_case)
 */
export interface AuxiliaryUpdateResponse {
  id: string
  auxiliar_name: string
  auxiliar_code: string
  auxiliar_email: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}

/**
 * Resultado de validación del formulario de edición
 */
export interface AuxiliaryEditFormValidation {
  isValid: boolean
  errors: {
    auxiliarName?: string
    auxiliarCode?: string
    AuxiliarEmail?: string
    observaciones?: string
  }
}
