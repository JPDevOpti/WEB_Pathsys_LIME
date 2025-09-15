import type { CaseModel, CaseListItem, CaseStatistics, CaseState } from './case'

export interface CreateCaseRequest {
  paciente: {
    paciente_code: string
    nombre: string
    edad: number
    sexo: string
    entidad_info: { id: string; nombre: string }
    tipo_atencion: string
    observaciones?: string
  }
  medico_solicitante?: string
  servicio?: string
  muestras: Array<{
    region_cuerpo: string
    pruebas: Array<{ id: string; nombre: string; cantidad: number }>
  }>
  estado: CaseState
  prioridad?: string
  observaciones_generales?: string
}

export interface UpdateCaseRequest {
  patologo_asignado?: { codigo: string; nombre: string }
  medico_solicitante?: string
  muestras?: Array<{
    region_cuerpo: string
    pruebas: Array<{ id: string; nombre: string; cantidad: number }>
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
  prioridad?: string
  observaciones_generales?: string
  entidad_info?: { id: string; nombre: string }
  paciente?: {
    paciente_code: string
    nombre: string
    edad: number
    sexo: string
    entidad_info: { id: string; nombre: string }
    tipo_atencion: string
    observaciones?: string
    fecha_actualizacion?: string
  }
}

export interface CreateCaseResponse {
  success: boolean
  message: string
  caso_code: string
  case: CaseModel
}
export interface UpdateCaseResponse extends CaseModel {}

export interface CaseListResponse {
  casos: CaseListItem[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

export interface CaseSearchResponse extends CaseListResponse {}
export interface CaseStatisticsResponse extends CaseStatistics {}

export interface DeleteCaseResponse {
  message: string
  CasoCode: string
  eliminado: boolean
}

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

export interface CaseListParams {
  skip?: number
  limit?: number
  estado?: CaseState
}

export interface ApiError {
  detail?: string
  message?: string
  errors?: Record<string, string[]>
}

export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: ApiError
}
