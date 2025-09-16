import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  CasosPorMesResponse,
  CasoUrgente,
  DashboardMetrics,
  EstadisticasOportunidad,
  CaseStatus
} from '../types/dashboard.types'
import { CasePriority } from '../types/dashboard.types'

class DashboardApiService {
  private readonly baseUrl = API_CONFIG.ENDPOINTS


  async getMetricasDashboard(): Promise<DashboardMetrics> {
    return this._getMetricas(`${this.baseUrl.CASES}/estadisticas/mes-actual`, { no_cache: true })
  }

  async getMetricasPatologo(): Promise<DashboardMetrics> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const code = (authStore.user as any)?.patologo_code || ''
      return this._getMetricas(`${this.baseUrl.CASES}/estadisticas/mes-actual/patologo`, { patologo_codigo: code, no_cache: true })
    } catch {
      return this.getMetricasDashboard()
    }
  }

  private async _getMetricas(url: string, params?: any): Promise<DashboardMetrics> {
    try {
      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      return {
        pacientes: {
          mes_actual: Number(data?.pacientes?.mes_actual ?? 0),
          mes_anterior: Number(data?.pacientes?.mes_anterior ?? 0),
          cambio_porcentual: Number(data?.pacientes?.cambio_porcentual ?? 0)
        },
        casos: {
          mes_actual: Number(data?.casos?.mes_actual ?? 0),
          mes_anterior: Number(data?.casos?.mes_anterior ?? 0),
          cambio_porcentual: Number(data?.casos?.cambio_porcentual ?? 0)
        }
      }
    } catch {
      return { pacientes: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 }, casos: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 } }
    }
  }

  async getCasosPorMes(año?: number): Promise<CasosPorMesResponse> {
    return this._getCasosPorMes(`${this.baseUrl.CASES}/estadisticas/por-mes/${año || new Date().getFullYear()}`, { no_cache: true })
  }

  async getCasosPorMesPatologo(año?: number): Promise<CasosPorMesResponse> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const code = (authStore.user as any)?.patologo_code || ''
      return this._getCasosPorMes(`${this.baseUrl.CASES}/estadisticas/por-mes/patologo/${año || new Date().getFullYear()}`, { patologo_codigo: code, no_cache: true })
    } catch {
      return this.getCasosPorMes(año)
    }
  }

  private async _getCasosPorMes(url: string, params?: any): Promise<CasosPorMesResponse> {
    const añoActual = new Date().getFullYear()
    const defaultResponse = { datos: Array(12).fill(0), total: 0, año: añoActual }

    try {
      if (añoActual < 2020 || añoActual > 2030) return defaultResponse

      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      
      if (!data || !Array.isArray(data.datos) || data.datos.length !== 12) return defaultResponse
      
      return { datos: data.datos, total: data.total || 0, año: data.año || añoActual }
    } catch {
      return defaultResponse
    }
  }

  async getUrgentCasesGeneral(limite: number = 50): Promise<CasoUrgente[]> {
    return this._getUrgentCases(`${this.baseUrl.CASES}/consulta/urgentes`, { limite })
  }

  async getUrgentCasesByPathologist(patologo_code: string, limite: number = 50): Promise<CasoUrgente[]> {
    return this._getUrgentCases(`${this.baseUrl.CASES}/consulta/urgentes/patologo`, { patologo_code, limite })
  }

  private async _getUrgentCases(url: string, params: any): Promise<CasoUrgente[]> {
    try {
      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      return this.transformarCasosUrgentesOptimizados(data.casos || [])
    } catch {
      return []
    }
  }


  async getEstadisticasOportunidad(): Promise<EstadisticasOportunidad> {
    return this._getEstadisticasOportunidad(`${this.baseUrl.CASES}/estadisticas/oportunidad/mes-anterior`)
  }

  async getEstadisticasOportunidadPatologo(): Promise<EstadisticasOportunidad> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const patCode = (authStore.user as any)?.patologo_code || ''
      return this._getEstadisticasOportunidad(`${this.baseUrl.CASES}/estadisticas/oportunidad/mes-anterior/patologo`, { patologo_codigo: patCode })
    } catch {
      return this.getEstadisticasOportunidad()
    }
  }

  private async _getEstadisticasOportunidad(url: string, params?: any): Promise<EstadisticasOportunidad> {
    const defaultResponse = {
      porcentaje_oportunidad: 0, cambio_porcentual: 0, tiempo_promedio: 0,
      casos_dentro_oportunidad: 0, casos_fuera_oportunidad: 0, total_casos_mes_anterior: 0,
      mes_anterior: { nombre: 'Mes anterior', inicio: '', fin: '' }
    }

    try {
      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      
      return {
        porcentaje_oportunidad: typeof data?.porcentaje_oportunidad === 'number' ? data.porcentaje_oportunidad : 0,
        cambio_porcentual: typeof data?.cambio_porcentual === 'number' ? data.cambio_porcentual : 0,
        tiempo_promedio: typeof data?.tiempo_promedio === 'number' ? data.tiempo_promedio : 0,
        casos_dentro_oportunidad: typeof data?.casos_dentro_oportunidad === 'number' ? data.casos_dentro_oportunidad : 0,
        casos_fuera_oportunidad: typeof data?.casos_fuera_oportunidad === 'number' ? data.casos_fuera_oportunidad : 0,
        total_casos_mes_anterior: typeof data?.total_casos_mes_anterior === 'number' ? data.total_casos_mes_anterior : 0,
        mes_anterior: {
          nombre: data?.mes_anterior?.nombre || 'Mes anterior',
          inicio: data?.mes_anterior?.inicio || '',
          fin: data?.mes_anterior?.fin || ''
        }
      }
    } catch {
      return defaultResponse
    }
  }

  private transformarCasosUrgentesOptimizados(casos: any[]): CasoUrgente[] {
    return casos.map((caso: any) => ({
      codigo: caso.caso_code || 'N/A',
      paciente: {
        nombre: caso.paciente_nombre || 'N/A',
        cedula: caso.paciente_documento || 'N/A',
        entidad: caso.entidad_nombre || 'Sin entidad'
      },
      pruebas: caso.pruebas || [],
      patologo: caso.patologo_nombre || 'Sin asignar',
      fecha_creacion: caso.fecha_creacion,
      estado: caso.estado as CaseStatus,
      prioridad: (caso.prioridad as CasePriority) || CasePriority.Normal,
      dias_en_sistema: caso.dias_habiles_transcurridos || 0
    }))
  }

}

export const dashboardApiService = new DashboardApiService()
export default dashboardApiService