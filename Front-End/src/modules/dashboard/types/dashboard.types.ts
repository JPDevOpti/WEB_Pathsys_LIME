export enum CasePriority {
  Normal = 'Normal',
  Prioritario = 'Prioritario'
}

export enum CaseStatus {
  EnProceso = 'En proceso',
  PorFirmar = 'Por firmar',
  PorEntregar = 'Por entregar',
  Completado = 'Completado'
}
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

export interface FiltrosCasosUrgentes {
  patologo?: string
  limite?: number
}

export interface CasosPorMesResponse {
  datos: number[]
  total: number
  año: number
}