import { CASE_STATES, ATTENTION_TYPES, GENDER_OPTIONS } from '@/core/config/api.config'

export type CaseState = typeof CASE_STATES[keyof typeof CASE_STATES]
export type AttentionType = typeof ATTENTION_TYPES[keyof typeof ATTENTION_TYPES]
export type Gender = typeof GENDER_OPTIONS[keyof typeof GENDER_OPTIONS]

export enum CasePriority {
  NORMAL = 'Normal',
  PRIORITARIO = 'Prioritario'
}

export interface EntityInfo {
  codigo: string
  nombre: string
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
  codigo: string
  nombre: string
}

export interface CaseResult {
  tipo_resultado?: string
  resultado_macro?: string
  resultado_micro?: string
  diagnostico?: string
  firmado?: boolean
  fecha_firma?: string
  patologo_firma?: string
  diagnostico_cie10?: { codigo: string; nombre: string }
  diagnostico_cieo?: { codigo: string; nombre: string }
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
  patologo_asignado?: PathologistInfo
  assigned_pathologist?: PathologistInfo
  entidad_info?: EntityInfo
  resultado?: CaseResult
  creado_por?: string
  actualizado_por?: string
  activo?: boolean
  // Campos en español para compatibilidad
  _id?: string
  caso_code?: string
  paciente?: PatientInfo
  medico_solicitante?: string
  servicio?: string
  muestras?: SampleInfo[]
  estado?: CaseState
  prioridad?: CasePriority
  fecha_ingreso?: string
  fecha_firma?: string
  fecha_actualizacion?: string
  observaciones_generales?: string
}

export interface CaseListItem {
  _id: string
  caso_code: string
  paciente: { nombre: string; cedula: string }
  estado: CaseState
  fecha_ingreso: string
  patologo_asignado?: { nombre: string }
}

export interface CaseStatistics {
  total_casos: number
  casos_pendientes: number
  casos_en_proceso: number
  casos_completados: number
  casos_entregados: number
  casos_cancelados: number
  casos_vencidos: number
  casos_sin_patologo: number
}
