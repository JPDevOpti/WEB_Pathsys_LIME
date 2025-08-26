export interface TestStats {
  codigo: string
  nombre: string
  solicitadas: number
  completadas: number
  tiempoPromedio: number
}

export interface TestsReportData {
  tests: TestStats[]
  summary?: {
    totalSolicitadas: number
    totalCompletadas: number
    tiempoPromedio: number
  }
}

export interface PeriodSelection {
  month: number
  year: number
}

export interface EntitySelection {
  codigo: string
  nombre: string
}

export interface TestDetails {
  estadisticas_principales: {
    total_solicitadas: number
    total_completadas: number
    porcentaje_completado: number
  }
  tiempos_procesamiento: {
    promedio_dias: number
    dentro_oportunidad: number
    fuera_oportunidad: number
    total_casos: number
  }
  patologos: Array<{
    nombre: string
    codigo: string
    total_procesadas: number
    tiempo_promedio: number
  }>
}

// Tipos para respuestas de la API
export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface BackendError {
  detail: string
  status_code?: number
  type?: string
}

// Tipos para las respuestas específicas del backend
export interface BackendTestStats {
  codigo: string
  nombre: string
  total_solicitadas: number
  total_completadas: number
  tiempo_promedio: number
  porcentaje_completado: number
}

export interface BackendTestDetails {
  estadisticas_principales: {
    total_solicitadas: number
    total_completadas: number
    porcentaje_completado: number
  }
  tiempos_procesamiento: {
    promedio_dias: number
    dentro_oportunidad: number
    fuera_oportunidad: number
    total_casos: number
  }
  patologos: Array<{
    nombre: string
    codigo: string
    total_procesadas: number
    tiempo_promedio: number
  }>
}