import { CASE_STATES, ATTENTION_TYPES, GENDER_OPTIONS } from '@/core/config/api.config'

export type CaseState = typeof CASE_STATES[keyof typeof CASE_STATES]
export type AttentionType = typeof ATTENTION_TYPES[keyof typeof ATTENTION_TYPES]
export type Gender = typeof GENDER_OPTIONS[keyof typeof GENDER_OPTIONS]

export enum CasePriority {
  NORMAL = 'Normal',
  PRIORITARIO = 'Prioritario'
}

export interface EntityInfo {
  id: string
  name: string
}

export interface PatientInfo {
  patient_code: string
  name: string
  age: number
  gender: Gender
  entity_info: EntityInfo
  care_type: AttentionType
  observations?: string
  updated_at?: string
  // Campos en español para compatibilidad
  paciente_code?: string
  nombre?: string
  edad?: number
  sexo?: Gender
  entidad_info?: EntityInfo
  tipo_atencion?: AttentionType
  fecha_actualizacion?: string
}

export interface DoctorInfo {
  nombre: string
}

export interface TestInfo {
  id: string
  name: string
  quantity?: number
  // Campos en español para compatibilidad
  nombre?: string
  cantidad?: number
}

export interface SampleInfo {
  body_region: string
  tests: TestInfo[]
  // Campos en español para compatibilidad
  region_cuerpo?: string
  pruebas?: TestInfo[]
}

export interface PathologistInfo {
  id: string
  name: string
}

export interface CaseResult {
  method?: string[]
  macro_result?: string
  micro_result?: string
  diagnosis?: string
  observations?: string
}

export interface CaseModel {
  id?: string
  case_code: string
  patient_info: PatientInfo
  requesting_physician?: string
  service?: string
  samples: SampleInfo[]
  state: CaseState
  priority?: CasePriority
  created_at: string
  updated_at: string
  observations?: string
  assigned_pathologist?: PathologistInfo
  entity_info?: EntityInfo
  result?: CaseResult
  created_by?: string
  updated_by?: string
  active?: boolean
}

export interface CaseListItem {
  _id: string
  case_code: string
  patient: { name: string; patient_code: string }
  state: CaseState
  created_at: string
  assigned_pathologist?: { name: string }
}

export interface CaseStatistics {
  total_cases: number
  pending_cases: number
  in_progress_cases: number
  completed_cases: number
  delivered_cases: number
  cancelled_cases: number
  expired_cases: number
  cases_without_pathologist: number
}
