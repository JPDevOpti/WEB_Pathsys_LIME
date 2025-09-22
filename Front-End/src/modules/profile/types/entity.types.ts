/**
 * Tipos específicos para la gestión de entidades en el módulo profile
 */

/**
 * Modelo del formulario de creación de entidades
 */
export interface EntityFormModel {
  entityName: string
  entityCode: string
  notes: string
  isActive: boolean
}

/**
 * Request para crear una nueva entidad
 */
export interface EntityCreateRequest {
  name: string
  entity_code: string
  notes: string
  is_active: boolean
}

/**
 * Response de creación de entidad
 */
export interface EntityCreateResponse {
  id: string
  name: string
  entity_code: string
  notes: string
  is_active: boolean
  created_at: string
  updated_at?: string
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
    entityName?: string
    entityCode?: string
    notes?: string
  }
}

/**
 * Modelo de edición de entidad
 */
export interface EntityEditFormModel {
  id: string
  entityName: string
  entityCode: string
  notes: string
  isActive: boolean
}

/**
 * Request para actualizar una entidad
 */
export interface EntityUpdateRequest {
  name?: string
  entity_code?: string
  notes?: string
  is_active?: boolean
}

/**
 * Response de actualización de entidad
 */
export interface EntityUpdateResponse {
  id: string
  name: string
  entity_code: string
  notes: string
  is_active: boolean
  created_at: string
  updated_at: string
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
    entityName?: string
    entityCode?: string
    notes?: string
  }
}
