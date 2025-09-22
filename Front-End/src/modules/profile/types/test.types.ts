/**
 * Tipos específicos para la gestión de pruebas en el módulo profile
 */

/**
 * Modelo del formulario de creación de pruebas
 */
export interface TestFormModel {
  testCode: string
  testName: string
  testDescription: string
  timeDays: number // Tiempo en días
  price: number // Precio de la prueba
  isActive: boolean
}

/**
 * Request para crear una nueva prueba
 */
export interface TestCreateRequest {
  test_code: string
  name: string
  description: string
  time: number // Tiempo en días
  price: number // Precio de la prueba
  is_active: boolean
}

/**
 * Response de creación de prueba
 */
export interface TestCreateResponse {
  _id: string
  test_code: string
  name: string
  description: string
  time: number // Tiempo en días
  price: number // Precio de la prueba
  is_active: boolean
  created_at: string
  updated_at?: string
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
    testCode?: string
    testName?: string
    testDescription?: string
    timeDays?: string
    price?: string
  }
}

/**
 * Modelo del formulario de edición de pruebas
 */
export interface TestEditFormModel {
  id: string
  testCode: string
  testName: string
  testDescription: string
  timeDays: number // Tiempo en días
  price: number // Precio de la prueba
  isActive: boolean
}

/**
 * Request para actualizar una prueba existente
 */
export interface TestUpdateRequest {
  test_code?: string
  name?: string
  description?: string
  time?: number // Tiempo en minutos
  price?: number // Precio de la prueba
  is_active?: boolean
}

/**
 * Response de actualización de prueba
 */
export interface TestUpdateResponse {
  _id: string
  test_code: string
  name: string
  description: string
  time: number // Tiempo en días
  price: number // Precio de la prueba
  is_active: boolean
  created_at: string
  updated_at: string
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
    testCode?: string
    testName?: string
    testDescription?: string
    timeDays?: string
    price?: string
  }
}

/**
 * Nota: El campo tiempo se maneja en días para coincidir con el backend
 * El backend valida que el tiempo esté entre 1 y 365 días
 */
