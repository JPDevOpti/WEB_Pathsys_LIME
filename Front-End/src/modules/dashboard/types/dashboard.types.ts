/**
 * Tipos para el módulo de dashboard
 */

// Enum para prioridad de casos
export enum CasePriority {
  Normal = 'Normal',
  Prioritario = 'Prioritario'
}

// Enum para estados de casos
export enum CaseStatus {
  EnProceso = 'En proceso',
  PorFirmar = 'Por firmar',
  PorEntregar = 'Por entregar',
  Completado = 'Completado'
}

// Estadísticas de pacientes
export interface PacienteStats {
  total_pacientes: number
  pacientes_mes_actual: number
  pacientes_mes_anterior: number
  cambio_porcentual: number
  promedio_edad: number
  distribucion_genero: {
    masculino: number
    femenino: number
    otro: number
  }
}

// Estadísticas de casos actualizadas según la documentación del backend
export interface CasoStats {
  total_casos: number
  casos_en_proceso: number
  casos_por_firmar: number
  casos_por_entregar: number
  casos_completados: number
  casos_vencidos: number
  casos_sin_patologo: number
  tiempo_promedio_procesamiento: number | null
  casos_mes_actual: number
  casos_mes_anterior: number
  casos_semana_actual: number
  cambio_porcentual: number
  casos_por_patologo: Record<string, number>
  casos_por_tipo_prueba: Record<string, number>
}

// Estadísticas de casos por mes
export interface CasosPorMes {
  mes: number
  año: number
  total_casos: number
}

// Caso urgente actualizado con prioridad
export interface CasoUrgente {
  codigo: string
  paciente: {
    nombre: string
    cedula: string
    entidad?: string
  }
  pruebas: string[]
  patologo: string
  fecha_creacion: string
  estado: CaseStatus
  prioridad: CasePriority
  dias_en_sistema: number
}

// Métricas del dashboard
export interface DashboardMetrics {
  pacientes: {
    mes_actual: number
    mes_anterior: number
    mes_anterior_anterior?: number
    cambio_porcentual: number
  }
  casos: {
    mes_actual: number
    mes_anterior: number
    mes_anterior_anterior?: number
    cambio_porcentual: number
  }
}

// Estadísticas de oportunidad
export interface EstadisticasOportunidad {
  porcentaje_oportunidad: number
  cambio_porcentual: number
  tiempo_promedio: number
  casos_dentro_oportunidad: number
  casos_fuera_oportunidad: number
  total_casos_mes_anterior: number
  mes_anterior: {
    nombre: string
    inicio: string
    fin: string
  }
}

// Filtros para casos urgentes actualizados
export interface FiltrosCasosUrgentes {
  patologo?: string
  estado?: CaseStatus
  prioridad?: CasePriority
  dias_minimos?: number
  limite?: number
}

// Estadísticas por prioridad
export interface EstadisticasPorPrioridad {
  [CasePriority.Normal]: number
  [CasePriority.Prioritario]: number
}

// Respuesta de la API para casos por mes
export interface CasosPorMesResponse {
  datos: number[]
  total: number
  año: number
}

// Estadísticas de muestras
export interface MuestraStats {
  total_muestras: number
  muestras_mes_anterior: number
  muestras_mes_anterior_anterior: number
  cambio_porcentual: number
  muestras_por_region: Record<string, number>
  muestras_por_tipo_prueba: Record<string, number>
  tiempo_promedio_procesamiento?: number
}