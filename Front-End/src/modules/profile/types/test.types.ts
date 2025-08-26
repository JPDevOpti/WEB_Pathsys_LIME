/**
 * Tipos específicos para la gestión de pruebas en el módulo profile
 */

/**
 * Modelo del formulario de creación de pruebas
 */
export interface TestFormModel {
  pruebaCode: string
  pruebasName: string
  pruebasDescription: string
  tiempo: number // Tiempo en días
  isActive: boolean
}

/**
 * Request para crear una nueva prueba
 */
export interface TestCreateRequest {
  pruebaCode: string
  pruebasName: string
  pruebasDescription: string
  tiempo: number // Tiempo en días
  isActive: boolean
}

/**
 * Response de creación de prueba
 */
export interface TestCreateResponse {
  id: string
  pruebaCode: string
  pruebasName: string
  pruebasDescription: string
  tiempo: number // Tiempo en días
  isActive: boolean
  fecha_creacion: string
  fecha_actualizacion?: string
}

/**
 * Estado de la operación de creación
 */
export interface TestCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario
 */
export interface TestFormValidation {
  isValid: boolean
  errors: {
    pruebaCode?: string
    pruebasName?: string
    pruebasDescription?: string
    tiempo?: string
  }
}

/**
 * Modelo del formulario de edición de pruebas
 */
export interface TestEditFormModel {
  id: string
  pruebaCode: string
  pruebasName: string
  pruebasDescription: string
  tiempo: number // Tiempo en días
  isActive: boolean
}

/**
 * Request para actualizar una prueba existente
 */
export interface TestUpdateRequest {
  pruebaCode?: string
  pruebasName?: string
  pruebasDescription?: string
  tiempo?: number // Tiempo en días
  isActive?: boolean
}

/**
 * Response de actualización de prueba
 */
export interface TestUpdateResponse {
  id: string
  pruebaCode: string
  pruebasName: string
  pruebasDescription: string
  tiempo: number // Tiempo en días
  isActive: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}

/**
 * Estado de la operación de edición
 */
export interface TestEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario de edición
 */
export interface TestEditFormValidation {
  isValid: boolean
  errors: {
    pruebaCode?: string
    pruebasName?: string
    pruebasDescription?: string
    tiempo?: string
  }
}

/**
 * Nota: El campo tiempo se maneja como input de texto
 * para permitir al usuario ingresar días directamente
 */
