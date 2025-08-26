export interface EntityStats {
  nombre: string
  codigo: string
  ambulatorios: number
  hospitalizados: number
  total: number
}

export interface EntitiesReportData {
  entities: EntityStats[]
  summary?: {
    total: number
    ambulatorios: number
    hospitalizados: number
    tiempoPromedio: number
  }
}

export interface PeriodSelection {
  month: number
  year: number
}

export interface EntityDetails {
  estadisticas_basicas: {
    total_pacientes: number
    ambulatorios: number
    hospitalizados: number
    promedio_muestras_por_paciente: number
  }
  tiempos_procesamiento: {
    promedio_dias: number
    minimo_dias: number
    maximo_dias: number
    muestras_completadas: number
  }
  pruebas_mas_solicitadas: Array<{
    codigo: string
    nombre?: string
    total_solicitudes: number
  }>
}

export interface EntityComparativa {
  nombre: string
  ambulatorios1: number
  hospitalizados1: number
  total1: number
  ambulatorios2: number
  hospitalizados2: number
  total2: number
  diferencia: number
}
