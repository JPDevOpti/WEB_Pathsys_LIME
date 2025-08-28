import { CASE_STATES, ATTENTION_TYPES, GENDER_OPTIONS } from '@/core/config/api.config'

export type CaseState = typeof CASE_STATES[keyof typeof CASE_STATES]
export type AttentionType = typeof ATTENTION_TYPES[keyof typeof ATTENTION_TYPES]
export type Gender = typeof GENDER_OPTIONS[keyof typeof GENDER_OPTIONS]

export interface EntityInfo {
  codigo: string
  nombre: string
}

export interface PatientInfo {
  paciente_code: string
  nombre: string
  edad: number
  sexo: Gender
  entidad_info: EntityInfo
  tipo_atencion: AttentionType
  observaciones?: string
  fecha_actualizacion: string
}

export interface DoctorInfo {
  nombre: string
}

export interface TestInfo {
  id: string
  nombre: string
}

export interface SampleInfo {
  region_cuerpo: string
  pruebas: TestInfo[]
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
  diagnostico_cie10?: { id: string; codigo: string; nombre: string }
  diagnostico_cieo?: { id: string; codigo: string; nombre: string }
}

export interface CaseModel {
  _id?: string
  CasoCode: string
  paciente: PatientInfo
  medico_solicitante?: DoctorInfo
  servicio?: string
  muestras: SampleInfo[]
  estado: CaseState
  fecha_ingreso: string
  fecha_firma?: string
  fecha_actualizacion: string
  observaciones_generales?: string
  patologo_asignado?: PathologistInfo
  entidad_info?: EntityInfo
  resultado?: CaseResult
  creado_por?: string
  actualizado_por?: string
  activo?: boolean
}

export interface CaseListItem {
  _id: string
  CasoCode: string
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
