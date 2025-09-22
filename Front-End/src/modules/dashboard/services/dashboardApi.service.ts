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
  // Deduplicate in-flight requests by URL+params
  private readonly inflight = new Map<string, Promise<any>>()
  // Cached pathologist code to avoid repeated dynamic imports
  private cachedPathologistCode: string | null = null

  // GET JSON with cache-busting and in-flight dedupe
  private async _getJson(url: string, params?: Record<string, unknown>): Promise<any> {
    const key = JSON.stringify({ url, params })
    const existing = this.inflight.get(key)
    if (existing) return existing
    const request = apiClient
      .get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      .then(r => (r?.data ?? r))
      .finally(() => this.inflight.delete(key))
    this.inflight.set(key, request)
    return request
  }

  // Resolve and memoize the current user's pathologist code
  private async _getPathologistCode(): Promise<string> {
    if (this.cachedPathologistCode !== null) return this.cachedPathologistCode
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      this.cachedPathologistCode = authStore.user?.pathologist_code || ''
      return this.cachedPathologistCode
    } catch {
      this.cachedPathologistCode = ''
      return ''
    }
  }


  async getMetricasDashboard(): Promise<DashboardMetrics> {
    return this._getMetricas(`${this.baseUrl.CASES}/statistics/metrics/general`, { no_cache: true })
  }

  async getMetricasPatologo(): Promise<DashboardMetrics> {
    try {
      const code = await this._getPathologistCode()

      if (!code) return this.getMetricasDashboard()

      return this._getMetricas(`${this.baseUrl.CASES}/statistics/metrics/pathologist/${code}`, { no_cache: true })
    } catch (error) {
      return this.getMetricasDashboard()
    }
  }

  // Fetch and normalize dashboard metrics
  private async _getMetricas(url: string, params?: any): Promise<DashboardMetrics> {
    try {
      const data = await this._getJson(url, params)
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
    return this._getCasosPorMes(`${this.baseUrl.CASES}/statistics/dashboard/cases-by-month/${año || new Date().getFullYear()}`, { no_cache: true })
  }

  async getCasosPorMesPatologo(año?: number): Promise<CasosPorMesResponse> {
    try {
      const code = await this._getPathologistCode()

      if (!code) return this.getCasosPorMes(año)

      return this._getCasosPorMes(`${this.baseUrl.CASES}/statistics/dashboard/cases-by-month/pathologist/${año || new Date().getFullYear()}`, { 
        pathologist_code: code, 
        no_cache: true 
      })
    } catch (error) {
      return this.getCasosPorMes(año)
    }
  }

  // Fetch monthly cases; ensure 12-length array and numeric totals
  private async _getCasosPorMes(url: string, params?: any): Promise<CasosPorMesResponse> {
    const añoActual = new Date().getFullYear()
    const defaultResponse: CasosPorMesResponse = { datos: Array(12).fill(0), total: 0, año: añoActual }

    try {
      const data = await this._getJson(url, params)

      if (!data || !Array.isArray(data.datos) || data.datos.length !== 12) {
        return defaultResponse
      }

      return { 
        datos: data.datos, 
        total: typeof data.total === 'number' ? data.total : 0, 
        año: typeof data.año === 'number' ? data.año : añoActual
      }
    } catch (error) {
      return defaultResponse
    }
  }

  async getUrgentCasesGeneral(limite: number = 50): Promise<CasoUrgente[]> {
    return this._getUrgentCases(`${this.baseUrl.CASES}/urgent`, { limit: limite, min_days: 6 })
  }

  async getUrgentCasesByPathologist(patologo_code: string, limite: number = 50): Promise<CasoUrgente[]> {
    return this._getUrgentCases(`${this.baseUrl.CASES}/urgent/pathologist`, { code: patologo_code, limit: limite, min_days: 6 })
  }

  // Fetch urgent cases; support both 'cases' (new) and 'casos' (compat)
  private async _getUrgentCases(url: string, params: any): Promise<CasoUrgente[]> {
    try {
      const data = await this._getJson(url, params)
      const items = Array.isArray(data?.cases) ? data.cases : (Array.isArray(data?.casos) ? data.casos : [])
      return this.transformarCasosUrgentesOptimizados(items)
    } catch {
      return []
    }
  }


  async getEstadisticasOportunidad(): Promise<EstadisticasOportunidad> {
    return this._getEstadisticasOportunidad(`${this.baseUrl.CASES}/statistics/opportunity/general`, { no_cache: true })
  }

  async getEstadisticasOportunidadPatologo(): Promise<EstadisticasOportunidad> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const code = authStore.user?.pathologist_code || ''

      if (!code) return this.getEstadisticasOportunidad()

      return this._getEstadisticasOportunidad(`${this.baseUrl.CASES}/statistics/opportunity/pathologist/${code}`, { no_cache: true })
    } catch (error) {
      return this.getEstadisticasOportunidad()
    }
  }

  // Fetch opportunity stats; handle nesting under 'oportunity'
  private async _getEstadisticasOportunidad(url: string, params?: any): Promise<EstadisticasOportunidad> {
    const defaultResponse = {
      porcentaje_oportunidad: 0, cambio_porcentual: 0, tiempo_promedio: 0,
      casos_dentro_oportunidad: 0, casos_fuera_oportunidad: 0, total_casos_mes_anterior: 0,
      mes_anterior: { nombre: 'Mes anterior', inicio: '', fin: '' }
    }

    try {
      const data = await this._getJson(url, params)

      const opportunityData = data?.oportunity || data

      return {
        porcentaje_oportunidad: typeof opportunityData?.porcentaje_oportunidad === 'number' ? opportunityData.porcentaje_oportunidad : 0,
        cambio_porcentual: typeof opportunityData?.cambio_porcentual === 'number' ? opportunityData.cambio_porcentual : 0,
        tiempo_promedio: typeof opportunityData?.tiempo_promedio === 'number' ? opportunityData.tiempo_promedio : 0,
        casos_dentro_oportunidad: typeof opportunityData?.casos_dentro_oportunidad === 'number' ? opportunityData.casos_dentro_oportunidad : 0,
        casos_fuera_oportunidad: typeof opportunityData?.casos_fuera_oportunidad === 'number' ? opportunityData.casos_fuera_oportunidad : 0,
        total_casos_mes_anterior: typeof opportunityData?.total_casos_mes_anterior === 'number' ? opportunityData.total_casos_mes_anterior : 0,
        mes_anterior: {
          nombre: opportunityData?.mes_anterior?.nombre || 'Mes anterior',
          inicio: opportunityData?.mes_anterior?.inicio || '',
          fin: opportunityData?.mes_anterior?.fin || ''
        }
      }
    } catch {
      return defaultResponse
    }
  }

  // Normalize urgent case items into app-friendly shape
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