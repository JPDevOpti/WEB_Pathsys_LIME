import type { CaseModel, CaseListItem, CaseStatistics, CaseState } from './case'

export interface CreateCaseRequest {
  patient_info: {
    patient_code: string
    name: string
    age: number
    gender: string
    entity_info: { id: string; name: string }
    care_type: string
    observations?: string
  }
  requesting_physician?: string
  service?: string
  samples: Array<{
    body_region: string
    tests: Array<{ id: string; name: string; quantity: number }>
  }>
  state: CaseState
  priority?: string
  observations?: string
}

export interface UpdateCaseRequest {
  assigned_pathologist?: { id: string; name: string } | null
  requesting_physician?: string
  samples?: Array<{
    body_region: string
    tests: Array<{ id: string; name?: string; quantity: number }>
  }>
  result?: {
    method?: string[]
    macro_result?: string
    micro_result?: string
    diagnosis?: string
    observations?: string
    signed?: boolean
    signed_at?: string
    signed_by?: string
  }
  state?: CaseState
  priority?: string
  observations?: string
  entity_info?: { id: string; name: string }
  patient_info?: {
    patient_code: string
    name: string
    age: number
    gender: string
    entity_info: { id: string; name: string }
    care_type: string
    observations?: string
    updated_at?: string
  }
}

export interface CreateCaseResponse {
  success: boolean
  message: string
  case_code: string
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
