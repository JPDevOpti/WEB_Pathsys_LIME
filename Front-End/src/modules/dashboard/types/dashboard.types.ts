/**
 * Tipos para el módulo de dashboard
 */

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

// Estadísticas de casos
export interface CasoStats {
  total_casos: number
  casos_mes_actual: number
  casos_mes_anterior: number
  cambio_porcentual: number
  casos_por_estado: {
    [estado: string]: number
  }
  casos_vencidos: number
  tiempo_promedio_procesamiento: number
}

// Estadísticas de casos por mes
export interface CasosPorMes {
  mes: number
  año: number
  total_casos: number
}

// Caso urgente
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
  estado: string
  dias_en_sistema: number
}

// Métricas del dashboard
export interface DashboardMetrics {
  pacientes: {
    mes_actual: number
    mes_anterior: number
    cambio_porcentual: number
  }
  casos: {
    mes_actual: number
    mes_anterior: number
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

// Filtros para casos urgentes
export interface FiltrosCasosUrgentes {
  patologo?: string
  estado?: string
  dias_minimos?: number
  limite?: number
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