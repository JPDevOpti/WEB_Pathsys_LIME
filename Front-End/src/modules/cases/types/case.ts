import { CASE_STATES, ATTENTION_TYPES, GENDER_OPTIONS } from '@/core/config/api.config'

// ============================================================================
// TIPOS BÁSICOS
// ============================================================================

/**
 * Tipos de estado de caso
 */
export type CaseState = typeof CASE_STATES[keyof typeof CASE_STATES]

/**
 * Tipos de atención médica
 */
export type AttentionType = typeof ATTENTION_TYPES[keyof typeof ATTENTION_TYPES]

/**
 * Opciones de género
 */
export type Gender = typeof GENDER_OPTIONS[keyof typeof GENDER_OPTIONS]

// ============================================================================
// INTERFACES DE INFORMACIÓN
// ============================================================================

/**
 * Información de entidad de salud
 */
export interface EntityInfo {
  codigo: string
  nombre: string
}

/**
 * Información del paciente dentro del caso
 */
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

/**
 * Información del médico solicitante
 */
export interface DoctorInfo {
  nombre: string
}

/**
 * Información de una prueba médica
 */
export interface TestInfo {
  id: string
  nombre: string
}

/**
 * Información de una muestra
 */
export interface SampleInfo {
  region_cuerpo: string
  pruebas: TestInfo[]
}

/**
 * Información del patólogo asignado
 */
export interface PathologistInfo {
  codigo: string
  nombre: string
}

// ============================================================================
// INTERFACES DE RESULTADOS
// ============================================================================

/**
 * Resultado del caso médico
 */
export interface CaseResult {
  tipo_resultado?: string
  resultado_macro?: string
  resultado_micro?: string
  diagnostico?: string
  firmado?: boolean
  fecha_firma?: string
  patologo_firma?: string
  diagnostico_cie10?: {
    id: string
    codigo: string
    nombre: string
  }
  diagnostico_cieo?: {
    id: string
    codigo: string
    nombre: string
  }
}

// ============================================================================
// INTERFACES PRINCIPALES
// ============================================================================

/**
 * Modelo completo del caso médico (según backend)
 */
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

/**
 * Información básica del caso para listas
 */
export interface CaseListItem {
  _id: string
  CasoCode: string
  paciente: {
    nombre: string
    cedula: string
  }
  estado: CaseState
  fecha_ingreso: string
  patologo_asignado?: {
    nombre: string
  }
}

// ============================================================================
// INTERFACES DE ESTADÍSTICAS
// ============================================================================

/**
 * Estadísticas del sistema de casos
 */
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
