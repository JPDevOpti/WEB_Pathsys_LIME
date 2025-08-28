import type { CaseModel, CaseListItem, CaseStatistics, CaseState } from './case'

// ============================================================================
// INTERFACES DE REQUEST
// ============================================================================

/**
 * Request para crear un nuevo caso
 */
export interface CreateCaseRequest {
  paciente: {
    paciente_code: string  // ✅ REQUERIDO - Código único del paciente
    cedula: string      // ✅ REQUERIDO - Número de cédula
    nombre: string      // ✅ REQUERIDO - Nombre completo
    edad: number        // ✅ REQUERIDO - Edad del paciente
    sexo: string        // ✅ REQUERIDO - Sexo del paciente
    entidad_info: {     // ✅ REQUERIDO - Información de la entidad
      id: string        // ✅ REQUERIDO - Código de la entidad
      nombre: string    // ✅ REQUERIDO - Nombre de la entidad
    }
    tipo_atencion: string  // ✅ REQUERIDO - Tipo de atención
    observaciones?: string // ❌ OPCIONAL - Observaciones del paciente
  }
  medico_solicitante?: {
    nombre: string
  }
  servicio?: string
  muestras: Array<{
    region_cuerpo: string
    pruebas: Array<{
      id: string
      nombre: string
      cantidad: number
    }>
  }>
  estado: CaseState
  observaciones_generales?: string
}

/**
 * Request para actualizar un caso
 */
export interface UpdateCaseRequest {
  patologo_asignado?: {
    codigo: string
    nombre: string
  }
  medico_solicitante?: {
    nombre: string
  }
  muestras?: Array<{
    region_cuerpo: string
    pruebas: Array<{
      id: string
      nombre: string
      cantidad: number
    }>
  }>
  resultado?: {
    tipo_resultado?: string
    resultado_macro?: string
    resultado_micro?: string
    diagnostico?: string
    firmado?: boolean
    fecha_firma?: string
    patologo_firma?: string
  }
  estado?: CaseState
  observaciones_generales?: string
  // Campo permitido por el backend para actualizar la entidad del caso
  entidad_info?: {
    id: string
    nombre: string
  }
  // Permitir actualizar información del paciente dentro del caso
  paciente?: {
    paciente_code: string
    cedula: string
    nombre: string
    edad: number
    sexo: string
    entidad_info: {
      id: string
      nombre: string
    }
    tipo_atencion: string
    observaciones?: string
    fecha_actualizacion?: string
  }
}

// ============================================================================
// INTERFACES DE RESPONSE
// ============================================================================

/**
 * Response al crear un caso
 */
export interface CreateCaseResponse extends CaseModel {}

/**
 * Response al actualizar un caso
 */
export interface UpdateCaseResponse extends CaseModel {}

/**
 * Response de lista de casos con paginación
 */
export interface CaseListResponse {
  casos: CaseListItem[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

/**
 * Response de búsqueda avanzada
 */
export interface CaseSearchResponse extends CaseListResponse {}

/**
 * Response de estadísticas
 */
export interface CaseStatisticsResponse extends CaseStatistics {}

/**
 * Response estándar de eliminación
 */
export interface DeleteCaseResponse {
  message: string
  CasoCode: string
  eliminado: boolean
}

// ============================================================================
// INTERFACES DE PARÁMETROS
// ============================================================================

/**
 * Parámetros de búsqueda para casos
 */
export interface CaseSearchParams {
  query?: string
  CasoCode?: string
  estado?: CaseState
  paciente_cedula?: string
  paciente_nombre?: string
  medico_nombre?: string
  fecha_ingreso_desde?: string
  fecha_ingreso_hasta?: string
  solo_vencidos?: boolean
  solo_sin_patologo?: boolean
  patologo_codigo?: string
  entidad_codigo?: string
  tiene_resultado?: boolean
  firmado?: boolean
  skip?: number
  limit?: number
}

/**
 * Parámetros de consulta para listar casos
 */
export interface CaseListParams {
  skip?: number
  limit?: number
  estado?: CaseState
}

// ============================================================================
// INTERFACES DE ERROR Y RESPUESTA GENÉRICA
// ============================================================================

/**
 * Error de API estructurado
 */
export interface ApiError {
  detail?: string
  message?: string
  errors?: Record<string, string[]>
}

/**
 * Response genérica de la API
 */
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: ApiError
}
