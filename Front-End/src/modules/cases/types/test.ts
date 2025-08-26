/**
 * Tipos para el manejo de pruebas médicas
 */

/**
 * Información básica de una prueba médica
 */
export interface TestDetails {
  id: string
  pruebaCode: string
  pruebasName: string
  pruebasDescription?: string
  tiempo?: number
  isActive: boolean
  fechaCreacion?: string
  fechaActualizacion?: string
}

/**
 * Parámetros de búsqueda para pruebas
 */
export interface TestSearchParams {
  query?: string
  activo?: boolean
  skip?: number
  limit?: number
}

/**
 * Response de lista de pruebas con paginación
 */
export interface TestListResponse {
  pruebas: TestDetails[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

/**
 * Resultado de operaciones con pruebas
 */
export interface TestOperationResult {
  success: boolean
  test?: TestDetails
  tests?: TestDetails[]
  message?: string
  error?: string
}

/**
 * Opción para selector de pruebas
 */
export interface TestSelectOption {
  value: string
  label: string
  description?: string
  time?: number
  test: TestDetails
}
