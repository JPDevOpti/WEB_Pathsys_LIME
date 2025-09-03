/**
 * Tipos específicos para la gestión de entidades en el módulo profile
 */

/**
 * Modelo del formulario de creación de entidades
 */
export interface EntityFormModel {
  EntidadName: string
  EntidadCode: string
  observaciones: string
  isActive: boolean
}

/**
 * Request para crear una nueva entidad
 */
export interface EntityCreateRequest {
  entidad_name: string
  entidad_code: string
  observaciones: string
  is_active: boolean
}

/**
 * Response de creación de entidad
 */
export interface EntityCreateResponse {
  id: string
  entidad_name: string
  entidad_code: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion?: string
}

/**
 * Estado de la operación de creación
 */
export interface EntityCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario
 */
export interface EntityFormValidation {
  isValid: boolean
  errors: {
    EntidadName?: string
    EntidadCode?: string
    observaciones?: string
  }
}

/**
 * Modelo de edición de entidad
 */
export interface EntityEditFormModel {
  id: string
  EntidadName: string
  EntidadCode: string
  observaciones: string
  isActive: boolean
}

/**
 * Request para actualizar una entidad
 */
export interface EntityUpdateRequest {
  entidad_name?: string
  entidad_code?: string
  observaciones?: string
  is_active?: boolean
}

/**
 * Response de actualización de entidad
 */
export interface EntityUpdateResponse {
  id: string
  entidad_name: string
  entidad_code: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}

/**
 * Estado de edición de entidad
 */
export interface EntityEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Validación del formulario de edición de entidad
 */
export interface EntityEditFormValidation {
  isValid: boolean
  errors: {
    EntidadName?: string
    EntidadCode?: string
    observaciones?: string
  }
}
