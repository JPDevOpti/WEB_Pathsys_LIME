// Priority levels for urgent cases
export enum CasePriority {
  Normal = 'Normal',
  Prioritario = 'Prioritario'
}

// High-level case status labels used across the dashboard
export enum CaseStatus {
  EnProceso = 'En proceso',
  PorFirmar = 'Por firmar',
  PorEntregar = 'Por entregar',
  Completado = 'Completado'
}
// Minimal shape for an urgent case item shown in the dashboard
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

// Aggregated KPI metrics for patients and cases
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
    cambio_porcentual: number
  }
}

// SLA opportunity statistics for last month period
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

// Optional filters for fetching urgent cases
export interface FiltrosCasosUrgentes {
  patologo?: string
  limite?: number
}

// Monthly cases time series response (12 data points)
export interface CasosPorMesResponse {
  datos: number[]
  total: number
  año: number
}